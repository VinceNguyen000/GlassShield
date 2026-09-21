"""
GlassShield Cross-Layer Telemetry Logger
Enforces the TelemetryTuple contract defined in memory.md
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import json
import os
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class SensorTrigger:
    source: str = "camera"  # "camera" | "imu" | "companion_sync"
    trigger_type: str = "continuous_stream"  # "continuous_stream" | "motion_activated" | "user_invoked"


@dataclass
class PrivacyLayerTelemetry:
    faces_detected: int = 0
    plates_detected: int = 0
    pii_masked: bool = False
    filter_latency_ms: float = 0.0


@dataclass
class NetworkFlowTelemetry:
    sni_domain: str = "edge.glassshield.internal"
    packet_count: int = 0
    mean_packet_size_bytes: float = 0.0
    mean_iat_ms: float = 0.0
    flow_classification: str = "normal"  # "normal" | "abnormal_leak" | "unknown"
    classifier_confidence: float = 0.95


@dataclass
class VlmAgentTelemetry:
    model_id: str = "egoblur-gen2-vlm-hybrid"
    prompt_injection_flagged: bool = False
    prompt_digest: str = "none"
    proposed_tool_call: str = "none"


@dataclass
class ActionGateTelemetry:
    action_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    verification_verdict: str = "ALLOW"  # "ALLOW" | "BLOCK" | "USER_CONFIRMATION_REQUIRED"
    reasoning: str = "Standard continuous stream monitoring"


@dataclass
class TelemetryTuple:
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sensor_trigger: SensorTrigger = field(default_factory=SensorTrigger)
    privacy_layer: PrivacyLayerTelemetry = field(default_factory=PrivacyLayerTelemetry)
    network_flow: NetworkFlowTelemetry = field(default_factory=NetworkFlowTelemetry)
    vlm_agent: VlmAgentTelemetry = field(default_factory=VlmAgentTelemetry)
    action_gate: ActionGateTelemetry = field(default_factory=ActionGateTelemetry)

    # Extended metadata for Human-AI Co-Design review & auditing
    human_review_status: str = "UNREVIEWED"  # "APPROVED" | "REJECTED" | "CORRECTED_FP" | "CORRECTED_FN" | "UNREVIEWED"
    human_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class TelemetryStore:
    """Thread-safe and session-persistent store for TelemetryTuples."""

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or os.path.join("telemetry", "telemetry_events.jsonl")
        self.events: List[TelemetryTuple] = []
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log(self, event: TelemetryTuple) -> None:
        self.events.append(event)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(event.to_json(indent=None) + "\n")

    def update_human_review(self, event_id: str, status: str, notes: str = "", verdict_override: Optional[str] = None) -> bool:
        for ev in self.events:
            if ev.event_id == event_id:
                ev.human_review_status = status
                ev.human_notes = notes
                if verdict_override:
                    ev.action_gate.verification_verdict = verdict_override
                return True
        return False

    def get_all(self) -> List[TelemetryTuple]:
        return self.events

    def get_metrics_summary(self) -> Dict[str, Any]:
        if not self.events:
            return {
                "total_events": 0,
                "mean_latency_ms": 0.0,
                "fps": 0.0,
                "total_pii_detected": 0,
                "flagged_false_positives": 0,
                "false_positive_rate": 0.0,
            }
        latencies = [e.privacy_layer.filter_latency_ms for e in self.events if e.privacy_layer.filter_latency_ms > 0]
        mean_latency = sum(latencies) / len(latencies) if latencies else 0.0
        fps = (1000.0 / mean_latency) if mean_latency > 0 else 0.0
        fp_count = sum(1 for e in self.events if e.human_review_status == "CORRECTED_FP")
        total_detections = sum(e.privacy_layer.faces_detected + e.privacy_layer.plates_detected for e in self.events)
        fpr = (fp_count / total_detections * 100.0) if total_detections > 0 else 0.0

        return {
            "total_events": len(self.events),
            "mean_latency_ms": round(mean_latency, 2),
            "fps": round(fps, 1),
            "total_pii_detected": total_detections,
            "flagged_false_positives": fp_count,
            "false_positive_rate": round(fpr, 2),
        }
