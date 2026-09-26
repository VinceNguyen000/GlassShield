"""
GlassShield Layer 03 & Downstream Reasoning Test Suite
Validates the End-to-End Workflow:
Encrypted Traffic Inference -> Grounded Policy RAG -> Defensible AI Reasoning -> Human Action Gate
"""

import os
import unittest
from layer_03_network_anomalies.meta_activity_engine import MetaActivityEngine
from layer_01_sensors_privacy.policy_rag import PolicyRAG
from layer_04_vlm_agent.ai_explainer import AIExplainer
from telemetry.telemetry_logger import (
    TelemetryTuple,
    TelemetryStore,
    SensorTrigger,
    PrivacyLayerTelemetry,
    NetworkFlowTelemetry,
    VlmAgentTelemetry,
    ActionGateTelemetry,
)


class TestNetworkMetaWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = MetaActivityEngine()
        cls.rag = PolicyRAG()
        cls.explainer = AIExplainer()
        cls.temp_log = "telemetry/test_network_meta_events.jsonl"
        cls.store = TelemetryStore(log_path=cls.temp_log)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_log):
            os.remove(cls.temp_log)

    def test_tcn01_exam_photo_ai_sequence_and_policy(self):
        """TC-N01: Exam trace -> [PHOTO -> AI_INTERACTION -> RESPONSE] -> POL-EXAM-3.2 -> BLOCK."""
        pkts = self.engine.generate_benchmark_trace("Exam Session: Camera Burst + Cloud LLM Query")
        res = self.engine.analyze_stream(pkts, optical_presence_enabled=True, optical_presence_detected=True)

        event_acts = [e.activity for e in res["events"]]
        self.assertIn("PHOTO", event_acts)
        self.assertIn("AI_INTERACTION", event_acts)
        self.assertIn("RESPONSE", event_acts)

        # Grounded RAG Retrieval
        policies = self.rag.retrieve(event_sequence=event_acts, top_k=2)
        self.assertEqual(policies[0]["id"], "POL-EXAM-3.2")
        self.assertIn("proctored", policies[0]["rule_text"].lower())

        # AI Explainer & Defensible Reasoning Contract
        exp = self.explainer.generate_network_meta_explanation(
            event_timeline_str=res["timeline_str"],
            events=res["events"],
            retrieved_policies=policies,
            optical_presence=res["optical_presence"],
            mean_uncertainty=res["mean_uncertainty"],
            abstention_count=res["abstention_count"],
        )
        self.assertEqual(exp["recommended_verdict"], "BLOCK")
        self.assertIn("POL-EXAM-3.2", exp["narrative"])
        # Ethical contract check: never accuse person of "cheating"
        self.assertNotIn("is cheating", exp["narrative"].lower())
        self.assertNotIn("guilty", exp["narrative"].lower())

    def test_tcn02_cleanroom_video_stream_and_policy(self):
        """TC-N02: Cleanroom video stream -> VIDEO/STREAM -> POL-LAB-REC-01 -> BLOCK."""
        pkts = self.engine.generate_benchmark_trace("Cleanroom R&D: Continuous Video Stream")
        res = self.engine.analyze_stream(pkts)

        event_acts = [e.activity for e in res["events"]]
        self.assertIn("VIDEO/STREAM", event_acts)

        policies = self.rag.retrieve(event_sequence=event_acts, top_k=2)
        self.assertEqual(policies[0]["id"], "POL-LAB-REC-01")

        exp = self.explainer.generate_network_meta_explanation(
            event_timeline_str=res["timeline_str"],
            events=res["events"],
            retrieved_policies=policies,
            optical_presence=res["optical_presence"],
            mean_uncertainty=res["mean_uncertainty"],
            abstention_count=res["abstention_count"],
        )
        self.assertEqual(exp["recommended_verdict"], "BLOCK")
        self.assertIn("POL-LAB-REC-01", exp["narrative"])

    def test_tcn03_open_set_abstention_on_jitter(self):
        """TC-N03: Adversarial jitter -> UNKNOWN (Abstention) -> USER_CONFIRMATION_REQUIRED."""
        pkts = self.engine.generate_benchmark_trace("Adversarial Jitter: Ambiguous Low-Confidence Stream")
        res = self.engine.analyze_stream(pkts, abstention_threshold=0.65)

        self.assertGreater(res["abstention_count"], 0)
        event_acts = [e.activity for e in res["events"]]
        self.assertIn("UNKNOWN", event_acts)

        policies = self.rag.retrieve(event_sequence=event_acts, top_k=2)
        exp = self.explainer.generate_network_meta_explanation(
            event_timeline_str=res["timeline_str"],
            events=res["events"],
            retrieved_policies=policies,
            optical_presence=res["optical_presence"],
            mean_uncertainty=res["mean_uncertainty"],
            abstention_count=res["abstention_count"],
        )
        self.assertEqual(exp["recommended_verdict"], "USER_CONFIRMATION_REQUIRED")
        self.assertIn("uncertainty", exp["gate_reasoning"].lower())

    def test_tcn04_optical_presence_fusion(self):
        """TC-N04: Non-content optical presence sensor corroboration."""
        pkts = self.engine.generate_benchmark_trace("Exam Session: Camera Burst + Cloud LLM Query")
        res = self.engine.analyze_stream(pkts, optical_presence_enabled=True, optical_presence_detected=True)

        self.assertTrue(res["optical_presence"]["enabled"])
        self.assertTrue(res["optical_presence"]["detected"])
        self.assertGreater(res["optical_presence"]["confidence"], 0.90)

    def test_tcn05_human_review_override_and_ledger(self):
        """TC-N05: Human Review Gate -> Override AI Verdict -> Update Telemetry Ledger."""
        pkts = self.engine.generate_benchmark_trace("Exam Session: Camera Burst + Cloud LLM Query")
        res = self.engine.analyze_stream(pkts)
        event_acts = [e.activity for e in res["events"]]
        policies = self.rag.retrieve(event_sequence=event_acts, top_k=1)
        exp = self.explainer.generate_network_meta_explanation(
            res["timeline_str"], res["events"], policies, res["optical_presence"], res["mean_uncertainty"], res["abstention_count"]
        )

        event = TelemetryTuple(
            network_flow=NetworkFlowTelemetry(
                packet_count=len(pkts),
                inferred_activity_sequence=event_acts,
                flow_classification="abnormal_leak",
            ),
            action_gate=ActionGateTelemetry(verification_verdict=exp["recommended_verdict"]),
        )
        self.store.log(event)

        # Human proctor reviews and overrides/approves
        updated = self.store.update_human_review(
            event.event_id,
            status="APPROVED",
            notes="Proctor confirmed prohibited exam photo query in Room 204",
            verdict_override="BLOCK",
        )
        self.assertTrue(updated)
        self.assertEqual(event.human_review_status, "APPROVED")
        self.assertEqual(event.action_gate.verification_verdict, "BLOCK")


if __name__ == "__main__":
    unittest.main()
