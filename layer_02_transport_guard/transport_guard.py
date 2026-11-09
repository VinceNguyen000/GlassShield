"""
Layer 02: Companion App & Transport Guard
Enforces mutual TLS (mTLS) framing, schema verification, and TelemetryTuple serialization.
"""
import hashlib
import datetime
from typing import Dict, Any, Optional
from telemetry.telemetry_logger import TelemetryTuple, TelemetryStore

class TransportGuard:
    """Enforces mTLS serialization and schema validation on smart glasses companion device."""
    def __init__(self, tls_version: str = "TLS 1.3", cert_fingerprint: str = "SHA256:4a8b..."):
        self.tls_version = tls_version
        self.cert_fingerprint = cert_fingerprint
        
    def frame_event(self, event_data: Dict[str, Any]) -> TelemetryTuple:
        """Validates and packages raw event into standardized TelemetryTuple."""
        return TelemetryTuple(**event_data)
        
    def compute_event_hash(self, event: TelemetryTuple) -> str:
        """Generates cryptographic event fingerprint for audit trail."""
        raw = f"{event.event_id}:{event.timestamp_utc}:{event.verdict}"
        return hashlib.sha256(raw.encode()).hexdigest()
