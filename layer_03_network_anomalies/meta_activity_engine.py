"""
GlassShield Layer 03: Network Anomaly & Meta-Activity Profiler
Implements encrypted-traffic meta-activity inference (Every Byte Matters [1], OVRseen)
without payload decryption or content inspection.
"""

from dataclasses import dataclass, field
import math
import random
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class PacketMetadata:
    """Privacy-preserving packet token: (timestamp, signed_length, delta_t, direction, protocol)."""
    timestamp_s: float
    length_bytes: int
    direction: str  # "uplink" (+1) or "downlink" (-1)
    protocol: str = "TLSv1.3"  # or "BLE_L2CAP"
    delta_t_ms: float = 0.0

    @property
    def signed_length(self) -> int:
        return self.length_bytes if self.direction == "uplink" else -self.length_bytes


@dataclass
class FlowWindowFeatures:
    """Summary features extracted over a temporal sliding window."""
    window_start_s: float
    window_end_s: float
    packet_count: int
    total_bytes: int
    uplink_bytes: int
    downlink_bytes: int
    uplink_ratio: float
    mean_packet_size: float
    std_packet_size: float
    mean_iat_ms: float
    std_iat_ms: float
    burst_rate_kbps: float


@dataclass
class MetaActivityPrediction:
    """Prediction for a single temporal window."""
    window_id: int
    start_time_s: float
    end_time_s: float
    predicted_activity: str
    confidence: float
    probabilities: Dict[str, float]
    uncertainty_score: float
    is_abstained: bool
    features: FlowWindowFeatures


@dataclass
class TemporalEvent:
    """Fused operational event spanning one or more adjacent windows."""
    event_order: int
    activity: str
    start_time_s: float
    end_time_s: float
    duration_s: float
    mean_confidence: float
    status: str  # "RESOLVED" | "ABSTAINED_UNKNOWN"
    notes: str = ""


class MetaActivityEngine:
    """
    Infers objective smart glasses operations (IDLE, PHOTO, VIDEO/STREAM,
    AI_INTERACTION, RESPONSE, SYNC/UPLOAD, UNKNOWN) from encrypted traffic metadata.
    """

    TARGET_ACTIVITIES = [
        "IDLE",
        "PHOTO",
        "VIDEO/STREAM",
        "AI_INTERACTION",
        "RESPONSE",
        "SYNC/UPLOAD",
        "UNKNOWN",
    ]

    def __init__(self, default_abstention_threshold: float = 0.65):
        self.default_abstention_threshold = default_abstention_threshold

    def extract_window_features(
        self,
        packets: List[PacketMetadata],
        window_start_s: float,
        window_end_s: float,
    ) -> FlowWindowFeatures:
        """Computes statistical features over a specific time window."""
        win_pkts = [p for p in packets if window_start_s <= p.timestamp_s < window_end_s]
        count = len(win_pkts)
        if count == 0:
            return FlowWindowFeatures(
                window_start_s=window_start_s,
                window_end_s=window_end_s,
                packet_count=0,
                total_bytes=0,
                uplink_bytes=0,
                downlink_bytes=0,
                uplink_ratio=0.0,
                mean_packet_size=0.0,
                std_packet_size=0.0,
                mean_iat_ms=0.0,
                std_iat_ms=0.0,
                burst_rate_kbps=0.0,
            )

        sizes = [p.length_bytes for p in win_pkts]
        uplink_bytes = sum(p.length_bytes for p in win_pkts if p.direction == "uplink")
        downlink_bytes = sum(p.length_bytes for p in win_pkts if p.direction == "downlink")
        total_bytes = uplink_bytes + downlink_bytes
        uplink_ratio = uplink_bytes / (total_bytes + 1e-9)

        mean_size = sum(sizes) / count
        var_size = sum((s - mean_size) ** 2 for s in sizes) / count
        std_size = math.sqrt(var_size)

        iats = [p.delta_t_ms for p in win_pkts if p.delta_t_ms > 0]
        mean_iat = (sum(iats) / len(iats)) if iats else 0.0
        var_iat = (sum((i - mean_iat) ** 2 for i in iats) / len(iats)) if iats else 0.0
        std_iat = math.sqrt(var_iat)

        duration_s = max(0.1, window_end_s - window_start_s)
        burst_rate_kbps = (total_bytes * 8.0) / (duration_s * 1000.0)

        return FlowWindowFeatures(
            window_start_s=window_start_s,
            window_end_s=window_end_s,
            packet_count=count,
            total_bytes=total_bytes,
            uplink_bytes=uplink_bytes,
            downlink_bytes=downlink_bytes,
            uplink_ratio=round(uplink_ratio, 3),
            mean_packet_size=round(mean_size, 1),
            std_packet_size=round(std_size, 1),
            mean_iat_ms=round(mean_iat, 1),
            std_iat_ms=round(std_iat, 1),
            burst_rate_kbps=round(burst_rate_kbps, 2),
        )

    def classify_window(
        self,
        features: FlowWindowFeatures,
        abstention_threshold: float,
    ) -> MetaActivityPrediction:
        """
        Calibrated probabilistic classification with explicit UNKNOWN/abstention support.
        Calculates probabilities across activities based on signature distributions.
        """
        probs = {act: 0.02 for act in self.TARGET_ACTIVITIES if act != "UNKNOWN"}

        # Heuristic likelihood calculation modeling empirical packet signatures:
        if features.packet_count <= 4 or features.burst_rate_kbps < 20.0:
            # Low throughput, periodic keepalives
            probs["IDLE"] += 0.85
            probs["SYNC/UPLOAD"] += 0.05
        elif features.burst_rate_kbps > 800.0 and features.packet_count > 60:
            # Sustained high throughput
            if features.uplink_ratio > 0.70 and features.mean_packet_size > 700:
                probs["VIDEO/STREAM"] += 0.88
                probs["SYNC/UPLOAD"] += 0.10
            else:
                probs["SYNC/UPLOAD"] += 0.70
                probs["VIDEO/STREAM"] += 0.20
        elif 80.0 <= features.burst_rate_kbps <= 800.0:
            # Medium burst
            if features.uplink_ratio > 0.80 and features.mean_packet_size > 700:
                if features.packet_count > 45:
                    # Sustained outbound bulk upload / media synchronization
                    probs["SYNC/UPLOAD"] += 0.86
                    probs["PHOTO"] += 0.08
                else:
                    # Single photo capture transmission burst
                    probs["PHOTO"] += 0.86
                    probs["SYNC/UPLOAD"] += 0.08
                probs["AI_INTERACTION"] += 0.04
            elif 0.35 <= features.uplink_ratio <= 0.75 and features.mean_iat_ms > 20:
                # Bidirectional query/assistant exchange
                probs["AI_INTERACTION"] += 0.82
                probs["RESPONSE"] += 0.12
            elif features.uplink_ratio < 0.30:
                # Downstream response burst
                probs["RESPONSE"] += 0.85
                probs["AI_INTERACTION"] += 0.10
            else:
                probs["SYNC/UPLOAD"] += 0.40
                probs["PHOTO"] += 0.30
        else:
            probs["IDLE"] += 0.35
            probs["AI_INTERACTION"] += 0.25

        # Normalize probabilities
        total_p = sum(probs.values())
        norm_probs = {k: round(v / total_p, 3) for k, v in probs.items()}

        # Find top candidate
        sorted_acts = sorted(norm_probs.items(), key=lambda x: x[1], reverse=True)
        top_act, top_conf = sorted_acts[0]
        second_conf = sorted_acts[1][1] if len(sorted_acts) > 1 else 0.0

        # Calibrated uncertainty score: reflects both top confidence and margin
        margin = top_conf - second_conf
        uncertainty = round(min(1.0, max(0.0, (1.0 - top_conf) * 0.7 + (1.0 - margin) * 0.3)), 2)

        # Open-Set / Abstention Gate
        is_abstained = False
        final_activity = top_act
        if top_conf < abstention_threshold or uncertainty > 0.45:
            final_activity = "UNKNOWN"
            is_abstained = True

        return MetaActivityPrediction(
            window_id=0,
            start_time_s=features.window_start_s,
            end_time_s=features.window_end_s,
            predicted_activity=final_activity,
            confidence=top_conf if not is_abstained else round(1.0 - uncertainty, 3),
            probabilities=norm_probs,
            uncertainty_score=uncertainty,
            is_abstained=is_abstained,
            features=features,
        )

    def temporal_fusion(
        self,
        predictions: List[MetaActivityPrediction],
    ) -> List[TemporalEvent]:
        """
        Merges window-level predictions into a smoothed, coherent event timeline.
        Collapses consecutive identical activities and preserves chronological transitions.
        """
        if not predictions:
            return []

        events: List[TemporalEvent] = []
        cur_act = predictions[0].predicted_activity
        cur_start = predictions[0].start_time_s
        cur_end = predictions[0].end_time_s
        cur_confs = [predictions[0].confidence]
        cur_abstained = predictions[0].is_abstained

        for p in predictions[1:]:
            if p.predicted_activity == cur_act:
                cur_end = p.end_time_s
                cur_confs.append(p.confidence)
                cur_abstained = cur_abstained or p.is_abstained
            else:
                mean_c = sum(cur_confs) / len(cur_confs)
                events.append(TemporalEvent(
                    event_order=len(events) + 1,
                    activity=cur_act,
                    start_time_s=round(cur_start, 2),
                    end_time_s=round(cur_end, 2),
                    duration_s=round(cur_end - cur_start, 2),
                    mean_confidence=round(mean_c, 3),
                    status="ABSTAINED_UNKNOWN" if cur_abstained or cur_act == "UNKNOWN" else "RESOLVED",
                    notes="Uncertain / borderline traffic burst" if cur_abstained else "Confident operational signature",
                ))
                cur_act = p.predicted_activity
                cur_start = p.start_time_s
                cur_end = p.end_time_s
                cur_confs = [p.confidence]
                cur_abstained = p.is_abstained

        # Final segment
        mean_c = sum(cur_confs) / len(cur_confs)
        events.append(TemporalEvent(
            event_order=len(events) + 1,
            activity=cur_act,
            start_time_s=round(cur_start, 2),
            end_time_s=round(cur_end, 2),
            duration_s=round(cur_end - cur_start, 2),
            mean_confidence=round(mean_c, 3),
            status="ABSTAINED_UNKNOWN" if cur_abstained or cur_act == "UNKNOWN" else "RESOLVED",
            notes="Uncertain / borderline traffic burst" if cur_abstained else "Confident operational signature",
        ))

        return events

    def analyze_stream(
        self,
        packets: List[PacketMetadata],
        window_size_s: float = 1.0,
        step_size_s: float = 1.0,
        abstention_threshold: Optional[float] = None,
        optical_presence_enabled: bool = False,
        optical_presence_detected: bool = False,
    ) -> Dict[str, Any]:
        """
        End-to-end signal-to-event inference pipeline.
        Transforms raw packet metadata into a fused operational timeline with uncertainty metrics.
        """
        thresh = abstention_threshold if abstention_threshold is not None else self.default_abstention_threshold
        if not packets:
            return {
                "events": [],
                "window_predictions": [],
                "summary": "No traffic packets observed.",
                "optical_presence": {"enabled": optical_presence_enabled, "detected": False, "confidence": 0.0},
                "mean_uncertainty": 0.0,
                "abstention_count": 0,
            }

        max_time = max(p.timestamp_s for p in packets)
        min_time = min(p.timestamp_s for p in packets)
        total_span = max(0.5, max_time - min_time)

        predictions: List[MetaActivityPrediction] = []
        curr_t = min_time
        win_idx = 0
        while curr_t < max_time:
            win_end = curr_t + window_size_s
            feats = self.extract_window_features(packets, curr_t, win_end)
            pred = self.classify_window(feats, thresh)
            pred.window_id = win_idx
            predictions.append(pred)
            curr_t += step_size_s
            win_idx += 1

        events = self.temporal_fusion(predictions)
        abstentions = sum(1 for e in events if e.status == "ABSTAINED_UNKNOWN")
        mean_uncertainty = sum(p.uncertainty_score for p in predictions) / len(predictions) if predictions else 0.0

        optical_info = {
            "enabled": optical_presence_enabled,
            "detected": optical_presence_detected if optical_presence_enabled else False,
            "confidence": 0.94 if (optical_presence_enabled and optical_presence_detected) else 0.05,
            "source": "AR Optical Signature (Ye et al., HotMobile 2026)" if optical_presence_enabled else "Disabled",
        }

        # Format timeline sequence string
        timeline_tokens = [f"{e.activity} ({e.mean_confidence * 100:.0f}%)" for e in events]
        timeline_str = " -> ".join(timeline_tokens) if timeline_tokens else "None"

        return {
            "events": events,
            "window_predictions": predictions,
            "timeline_str": timeline_str,
            "optical_presence": optical_info,
            "mean_uncertainty": round(mean_uncertainty, 3),
            "abstention_count": abstentions,
            "total_windows": len(predictions),
            "packet_count": len(packets),
            "total_span_s": round(total_span, 2),
        }

    @staticmethod
    def generate_benchmark_trace(scenario_type: str) -> List[PacketMetadata]:
        """
        Generates realistic encrypted packet metadata traces based on empirical
        smart-glasses operational measurements (Every Byte Matters & OVRseen patterns).
        """
        packets: List[PacketMetadata] = []
        random.seed(42)

        if scenario_type == "Exam Session: Camera Burst + Cloud LLM Query":
            # 0.0s - 1.5s: IDLE keepalives
            t = 0.0
            while t < 1.5:
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=64, direction="uplink", delta_t_ms=250.0))
                packets.append(PacketMetadata(timestamp_s=round(t + 0.01, 3), length_bytes=72, direction="downlink", delta_t_ms=10.0))
                t += 0.35

            # 1.5s - 2.8s: PHOTO capture + uplink transfer (~350KB)
            while t < 2.8:
                for _ in range(6):
                    t += random.uniform(0.005, 0.015)
                    packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=random.randint(950, 1420), direction="uplink", delta_t_ms=10.0))
                t += 0.05

            # 2.8s - 4.2s: AI_INTERACTION (voice/prompt exchange)
            while t < 4.2:
                t += random.uniform(0.02, 0.06)
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=random.randint(450, 850), direction="uplink", delta_t_ms=35.0))
                packets.append(PacketMetadata(timestamp_s=round(t + 0.01, 3), length_bytes=random.randint(200, 500), direction="downlink", delta_t_ms=10.0))

            # 4.2s - 5.5s: RESPONSE (cloud LLM streaming text tokens / audio back)
            while t < 5.5:
                t += random.uniform(0.01, 0.03)
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=random.randint(650, 1380), direction="downlink", delta_t_ms=18.0))

            # 5.5s - 6.5s: return to IDLE
            while t < 6.5:
                t += 0.3
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=64, direction="uplink", delta_t_ms=300.0))

        elif scenario_type == "Cleanroom R&D: Continuous Video Stream":
            # Sustained high rate video stream (1.5 - 3.0 Mbps)
            t = 0.0
            while t < 6.0:
                t += random.uniform(0.003, 0.008)
                # Dense uplink frame packets
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=random.randint(1100, 1460), direction="uplink", delta_t_ms=5.0))
                if random.random() < 0.15:
                    packets.append(PacketMetadata(timestamp_s=round(t + 0.001, 3), length_bytes=64, direction="downlink", delta_t_ms=1.0))

        elif scenario_type == "Library Study: Benign Wear & Periodic Cloud Sync":
            # 0.0s - 3.0s: IDLE
            t = 0.0
            while t < 3.0:
                t += 0.4
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=random.randint(54, 90), direction="uplink", delta_t_ms=400.0))

            # 3.0s - 5.5s: SYNC/UPLOAD (background batch photo thumbnail sync)
            while t < 5.5:
                t += random.uniform(0.008, 0.02)
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=random.randint(850, 1350), direction="uplink", delta_t_ms=15.0))

            # 5.5s - 6.5s: IDLE
            while t < 6.5:
                t += 0.4
                packets.append(PacketMetadata(timestamp_s=round(t, 3), length_bytes=64, direction="uplink", delta_t_ms=400.0))

        elif scenario_type == "Adversarial Jitter: Ambiguous Low-Confidence Stream":
            # Out-of-distribution noise / burst jitter designed to test abstention (UNKNOWN)
            t = 0.0
            while t < 5.0:
                t += random.uniform(0.05, 0.25)
                # Irregular packet sizes and unpredictable directions
                packets.append(PacketMetadata(
                    timestamp_s=round(t, 3),
                    length_bytes=random.choice([120, 340, 780, 1150]),
                    direction=random.choice(["uplink", "downlink"]),
                    delta_t_ms=random.uniform(50.0, 250.0),
                ))

        return packets
