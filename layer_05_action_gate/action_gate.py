"""
Layer 05: Action Gate & Safety Boundary
Enforces deterministic policy boundaries (ALLOW / BLOCK / CONFIRM) and calibrated abstention.
"""
from typing import Dict, Any, Optional

class GateVerdict:
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    CONFIRM = "USER_CONFIRMATION_REQUIRED"
    UNKNOWN = "UNKNOWN"

class ActionGate:
    """Deterministic Safety Boundary enforcing calibrated policy gating."""
    def __init__(self, uncertainty_threshold: float = 0.40):
        self.uncertainty_threshold = uncertainty_threshold
        
    def evaluate(self, uncertainty_score: float, risk_context: str, anomaly_detected: bool) -> str:
        """
        Calibrated open-set decision:
        If uncertainty exceeds threshold -> Abstain (UNKNOWN).
        If anomaly detected in restricted context -> BLOCK.
        Otherwise -> ALLOW.
        """
        if uncertainty_score >= self.uncertainty_threshold:
            return GateVerdict.UNKNOWN
            
        if anomaly_detected:
            if "exam" in risk_context.lower() or "cleanroom" in risk_context.lower():
                return GateVerdict.BLOCK
            return GateVerdict.CONFIRM
            
        return GateVerdict.ALLOW
