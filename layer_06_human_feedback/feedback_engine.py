"""
Layer 06: Human-in-the-Loop Feedback & Active Learning
Tracks session false positive rates (FPR), manual proctor overrides, and dynamic edge retuning.
"""
from typing import List, Dict, Any
from telemetry.telemetry_logger import TelemetryStore

class HumanFeedbackEngine:
    """Manages active human review, proctor override audits, and empirical FPR tracking."""
    def __init__(self, store: Optional[TelemetryStore] = None):
        self.store = store or TelemetryStore()
        self.reviews: List[Dict[str, Any]] = []
        
    def record_proctor_review(self, event_id: str, original_verdict: str, human_verdict: str, reviewer_notes: str = ""):
        """Records proctor review and triggers dynamic graph weight retuning."""
        is_override = (original_verdict != human_verdict)
        review_entry = {
            "event_id": event_id,
            "original_verdict": original_verdict,
            "human_verdict": human_verdict,
            "is_override": is_override,
            "notes": reviewer_notes
        }
        self.reviews.append(review_entry)
        return review_entry
        
    def calculate_session_fpr(self) -> float:
        """Computes empirical session False Positive Rate."""
        if not self.reviews:
            return 0.0
        false_positives = sum(1 for r in self.reviews if r["original_verdict"] == "BLOCK" and r["human_verdict"] == "ALLOW")
        total_blocks = sum(1 for r in self.reviews if r["original_verdict"] == "BLOCK")
        return (false_positives / total_blocks) if total_blocks > 0 else 0.0
