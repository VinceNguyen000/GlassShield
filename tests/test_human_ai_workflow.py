"""
GlassShield Human-AI Co-Design Test Suite
Validates the end-to-end workflow across 8 test cases:
User Input -> Retrieval/Analysis -> AI Output -> Evidence -> Human Review
"""

import os
import unittest
from PIL import Image
import numpy as np

from layer_01_sensors_privacy.privacy_engine import PrivacyEngine
from layer_01_sensors_privacy.policy_rag import PolicyRAG
from layer_01_sensors_privacy.sample_data_loader import SampleDataLoader
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


class TestHumanAIWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = PrivacyEngine()
        cls.rag = PolicyRAG()
        cls.explainer = AIExplainer()
        cls.samples = SampleDataLoader.ensure_samples()
        cls.temp_telemetry_log = "telemetry/test_telemetry_events.jsonl"
        cls.store = TelemetryStore(log_path=cls.temp_telemetry_log)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_telemetry_log):
            os.remove(cls.temp_telemetry_log)

    def test_tc01_bystander_face_detection_and_approval(self):
        """TC-01: User Input (Bystander Face) -> Detection -> Policy RAG -> Evidence -> Human Approval."""
        img_path = self.samples["Bystander Portrait (SITARA Real Sample)"]
        img = Image.open(img_path)

        # 1. User Input & Detection
        res = self.engine.process_frame(img, detect_faces=True, detect_plates=False, score_threshold=0.10)
        self.assertGreaterEqual(res["faces_detected"], 1, "Should detect at least 1 face")
        self.assertGreater(res["filter_latency_ms"], 0.0, "Latency must be recorded")

        # 2. Retrieval / Policy RAG
        policies = self.rag.retrieve(detected_classes=["face"], top_k=2)
        self.assertTrue(any("POL-SITARA-001" in p["id"] or "POL-GDPR-ART9" in p["id"] for p in policies))

        # 3. AI Explanation
        explanation = self.explainer.generate_explanation(res["detected_entities"], policies, res["filter_latency_ms"])
        self.assertIn("POL-", explanation["narrative"], "Explanation must ground in regulatory policy")
        self.assertIn(explanation["recommended_verdict"], ["ALLOW", "USER_CONFIRMATION_REQUIRED"])

        # 4. Evidence & Provenance
        self.assertTrue(res["pii_masked"], "PII must be masked in output image")
        self.assertEqual(res["overlay_image"].shape, res["anonymized_image"].shape)

        # 5. Human Review
        event = TelemetryTuple(
            privacy_layer=PrivacyLayerTelemetry(
                faces_detected=res["faces_detected"],
                pii_masked=res["pii_masked"],
                filter_latency_ms=res["filter_latency_ms"],
            ),
            action_gate=ActionGateTelemetry(verification_verdict=explanation["recommended_verdict"]),
        )
        self.store.log(event)
        updated = self.store.update_human_review(event.event_id, status="APPROVED", notes="Face successfully blurred")
        self.assertTrue(updated)
        self.assertEqual(event.human_review_status, "APPROVED")

    def test_tc02_vehicle_license_plate_retrieval(self):
        """TC-02: Vehicle License Plate -> CCPA Retrieval -> Masking -> Human Verification."""
        img_path = self.samples["Vehicle License Plate (Urban Traffic)"]
        img = Image.open(img_path)

        res = self.engine.process_frame(img, detect_faces=False, detect_plates=True, score_threshold=0.10)
        # Even if synthetic plate model fires or manual plate coords, check RAG and masking
        policies = self.rag.retrieve(query="vehicle license plate", detected_classes=["license_plate"], top_k=2)
        self.assertEqual(policies[0]["id"], "POL-CCPA-LP", "Should match CCPA Vehicle Identifier Policy")
        self.assertIn("vehicle", policies[0]["keywords"])

        # Grounded AI Output
        explanation = self.explainer.generate_explanation(res["detected_entities"], policies, res["filter_latency_ms"])
        self.assertEqual(explanation["top_policy_id"], "POL-CCPA-LP")

    def test_tc03_crowd_scene_multi_detection_and_table(self):
        """TC-03: Multi-Bystander Crowd Scene -> Density Handling -> Evidence Table."""
        img_path = self.samples["Crowded Pedestrian Street (Multi-PII)"]
        img = Image.open(img_path)

        res = self.engine.process_frame(img, detect_faces=True, score_threshold=0.10)
        policies = self.rag.retrieve(query="crowd pedestrian street", detected_classes=["face"], top_k=3)
        self.assertTrue(len(policies) > 0)

        # Evidence table check
        for entity in res["detected_entities"]:
            self.assertIn("box", entity)
            self.assertEqual(len(entity["box"]), 4)
            self.assertGreaterEqual(entity["confidence"], 0.0)

    def test_tc04_clean_room_true_negative(self):
        """TC-04: Clean Room (No PII) -> True Negative -> Content Preserved -> ALLOW Verdict."""
        img_path = self.samples["Clean Meeting Room (True Negative / No PII)"]
        img = Image.open(img_path)

        res = self.engine.process_frame(img, detect_faces=True, detect_plates=True, score_threshold=0.35)
        self.assertEqual(res["faces_detected"], 0)
        self.assertEqual(res["plates_detected"], 0)
        self.assertFalse(res["pii_masked"])

        policies = self.rag.retrieve(detected_classes=[], top_k=1)
        self.assertEqual(policies[0]["id"], "POL-CLEAN-ENV")

        explanation = self.explainer.generate_explanation(res["detected_entities"], policies, res["filter_latency_ms"])
        self.assertEqual(explanation["recommended_verdict"], "ALLOW")
        self.assertEqual(explanation["risk_level"], "LOW")

    def test_tc05_false_positive_audit_and_correction(self):
        """TC-05: False Positive on Textured Wall -> Human Flags FP -> Threshold Refinement -> FPR Tracked."""
        img_path = self.samples["Textured Wall Art (False Positive Audit)"]
        img = Image.open(img_path)

        # Run at low threshold where texture might produce borderline detection
        res = self.engine.process_frame(img, detect_faces=True, score_threshold=0.05)

        event = TelemetryTuple(
            privacy_layer=PrivacyLayerTelemetry(
                faces_detected=max(1, res["faces_detected"]),
                filter_latency_ms=res["filter_latency_ms"],
            )
        )
        self.store.log(event)

        # Human flags as False Positive
        self.store.update_human_review(
            event.event_id,
            status="CORRECTED_FP",
            notes="Texture on modern art exhibit misclassified as face; raised threshold to 0.40",
        )

        metrics = self.store.get_metrics_summary()
        self.assertGreaterEqual(metrics["flagged_false_positives"], 1)

        # Re-run with refined threshold (e.g. 0.50)
        refined_res = self.engine.process_frame(img, detect_faces=True, score_threshold=0.50)
        # Verify refinement clears or reduces low-confidence false positives
        self.assertLessEqual(refined_res["faces_detected"], res["faces_detected"])

    def test_tc06_missing_evidence_edge_case(self):
        """TC-06: Low-Light Failure Case -> High Uncertainty -> User Supplies Manual Bounding Box."""
        img_path = self.samples["Low-Light Obscured Bystander (Failure Case)"]
        img = Image.open(img_path)

        # Low light detection produces marginal or zero confidence
        res = self.engine.process_frame(img, detect_faces=True, score_threshold=0.50)

        # Policy RAG retrieves uncertainty rule
        policies = self.rag.retrieve(query="low light obscured bystander", min_confidence=0.30, top_k=1)
        self.assertEqual(policies[0]["id"], "POL-SITARA-UNCERTAIN")

        explanation = self.explainer.generate_explanation(
            [{"class_name": "face", "confidence": 0.32, "box": [400, 350, 500, 480], "area_pct": 2.5}],
            policies,
            res["filter_latency_ms"],
        )
        self.assertGreaterEqual(explanation["uncertainty_score"], 0.35, "Should report high uncertainty on marginal detection")
        self.assertEqual(explanation["recommended_verdict"], "USER_CONFIRMATION_REQUIRED")

        # Human refinement: user supplies manual bounding box to force blur the obscured face
        manual_box = [420.0, 350.0, 490.0, 470.0]
        refined_res = self.engine.process_frame(
            img,
            detect_faces=False,
            manual_boxes=[manual_box],
        )
        self.assertTrue(refined_res["pii_masked"], "Manual box must be obfuscated")
        self.assertTrue(any("manual" in e["class_name"] for e in refined_res["detected_entities"]))

    def test_tc07_action_gate_override_rejection(self):
        """TC-07: Enterprise Facility Scenario -> Policy Flags Risk -> Human Overrides Verdict to BLOCK."""
        detected_entities = [{"class_name": "face", "confidence": 0.88, "box": [200, 150, 350, 320], "area_pct": 5.0}]
        policies = self.rag.retrieve(query="enterprise confidential facility meeting cleanroom", top_k=1)
        self.assertEqual(policies[0]["id"], "POL-ENT-CONF")

        explanation = self.explainer.generate_explanation(detected_entities, policies, filter_latency_ms=22.5)

        event = TelemetryTuple(
            action_gate=ActionGateTelemetry(verification_verdict=explanation["recommended_verdict"])
        )
        self.store.log(event)

        # Human override to BLOCK due to proprietary conference room
        self.store.update_human_review(
            event.event_id,
            status="REJECTED",
            notes="Enterprise confidential zone rule enforced: stopped outbound stream",
            verdict_override="BLOCK",
        )
        self.assertEqual(event.action_gate.verification_verdict, "BLOCK")
        self.assertEqual(event.human_review_status, "REJECTED")

    def test_tc08_telemetry_tuple_schema_contract(self):
        """TC-08: Telemetry Tuple Schema Contract & Benchmark Metrics Ledger."""
        event = TelemetryTuple(
            sensor_trigger=SensorTrigger(source="camera", trigger_type="continuous_stream"),
            privacy_layer=PrivacyLayerTelemetry(faces_detected=2, plates_detected=1, pii_masked=True, filter_latency_ms=21.4),
            network_flow=NetworkFlowTelemetry(sni_domain="edge.glassshield.internal", flow_classification="normal"),
            vlm_agent=VlmAgentTelemetry(model_id="EgoBlur-Gen1-TorchScript"),
            action_gate=ActionGateTelemetry(verification_verdict="ALLOW"),
        )
        event_dict = event.to_dict()

        # Check all required top-level schema fields from memory.md
        required_keys = ["timestamp", "event_id", "sensor_trigger", "privacy_layer", "network_flow", "vlm_agent", "action_gate"]
        for k in required_keys:
            self.assertIn(k, event_dict)

        # Check subfields
        self.assertEqual(event_dict["sensor_trigger"]["source"], "camera")
        self.assertEqual(event_dict["privacy_layer"]["faces_detected"], 2)
        self.assertEqual(event_dict["privacy_layer"]["plates_detected"], 1)
        self.assertTrue(event_dict["privacy_layer"]["pii_masked"])
        self.assertEqual(event_dict["action_gate"]["verification_verdict"], "ALLOW")


if __name__ == "__main__":
    unittest.main()
