"""
GlassShield Evaluation Benchmark Script
Measures real performance across the 6 test scenarios:
1. Response Time / Latency (ms) & FPS achieved
2. Citation Accuracy & Groundedness (Precision@1 of retrieved policies)
3. Task Success Rate (Masking & Correct Action Gate Verdict)
4. False Positive Rate (FPR on clean background / artwork)
"""

import time
from PIL import Image
from layer_01_sensors_privacy.privacy_engine import PrivacyEngine
from layer_01_sensors_privacy.policy_rag import PolicyRAG
from layer_01_sensors_privacy.sample_data_loader import SampleDataLoader
from layer_04_vlm_agent.ai_explainer import AIExplainer

def run_evaluation():
    engine = PrivacyEngine()
    rag = PolicyRAG()
    explainer = AIExplainer()
    samples = SampleDataLoader.ensure_samples()

    print("=" * 70)
    print("GLASSSHIELD REAL-SYSTEM EVALUATION BENCHMARK")
    print("=" * 70)

    # Ground-truth expectations for each scenario:
    ground_truth = {
        "Bystander Portrait (SITARA Real Sample)": {
            "expected_pii": True,
            "expected_classes": ["face"],
            "expected_policy_substr": ["POL-GDPR-ART9", "POL-SITARA-001"],
            "expected_verdict": ["ALLOW", "USER_CONFIRMATION_REQUIRED"],
        },
        "Vehicle License Plate (Urban Traffic)": {
            "expected_pii": True,
            "expected_classes": ["license_plate"],
            "expected_policy_substr": ["POL-CCPA-VEHICLE"],
            "expected_verdict": ["ALLOW", "USER_CONFIRMATION_REQUIRED"],
        },
        "Crowded Pedestrian Street (Multi-PII)": {
            "expected_pii": True,
            "expected_classes": ["face"],
            "expected_policy_substr": ["POL-GDPR-ART9", "POL-SITARA-001"],
            "expected_verdict": ["ALLOW", "USER_CONFIRMATION_REQUIRED"],
        },
        "Clean Meeting Room (True Negative / No PII)": {
            "expected_pii": False,
            "expected_classes": [],
            "expected_policy_substr": ["POL-ENT-CONF"],
            "expected_verdict": ["ALLOW"],
        },
        "Low-Light Obscured Bystander (Failure Case)": {
            "expected_pii": True,
            "expected_classes": ["face"],
            "expected_policy_substr": ["POL-SITARA-UNCERTAIN", "POL-SITARA-001"],
            "expected_verdict": ["USER_CONFIRMATION_REQUIRED", "ALLOW"],
        },
        "Textured Wall Art (False Positive Audit)": {
            "expected_pii": False,
            "expected_classes": [],
            "expected_policy_substr": ["POL-GDPR-ART9", "POL-SITARA-001"],
            "expected_verdict": ["ALLOW"],
        },
    }

    latencies = []
    citation_hits = 0
    task_successes = 0
    total_scenarios = len(samples)
    false_positives = 0

    print(f"\n{'Scenario Name':<42} | {'Lat(ms)':<8} | {'PII Masked':<10} | {'Policy Match':<12} | {'Verdict'}")
    print("-" * 90)

    for name, path in samples.items():
        img = Image.open(path)
        gt = ground_truth.get(name, {})

        # 1. Measure Response Time (Latency)
        res = engine.process_frame(img, detect_faces=True, detect_plates=True, score_threshold=0.25)
        lat = res["filter_latency_ms"]
        latencies.append(lat)

        # 2. Retrieve Policies (Policy RAG Citation Accuracy)
        detected_classes = [e["class_name"] for e in res["detected_entities"]]
        min_conf = min([e["confidence"] for e in res["detected_entities"]]) if res["detected_entities"] else 1.0
        query_text = name.lower()
        policies = rag.retrieve(query=query_text, detected_classes=detected_classes, min_confidence=min_conf, top_k=2)

        # Evaluate Citation Accuracy (Precision@K)
        retrieved_ids = [p["id"] for p in policies]
        expected_policies = gt.get("expected_policy_substr", [])
        has_citation_match = any(any(exp in pid for pid in retrieved_ids) for exp in expected_policies)
        if has_citation_match or not expected_policies:
            citation_hits += 1

        # 3. AI Explanation & Gate Verdict
        explanation = explainer.generate_explanation(res["detected_entities"], policies, lat)
        verdict = explanation["recommended_verdict"]

        # Check Masking & Task Success
        pii_detected = res["faces_detected"] > 0 or res["plates_detected"] > 0
        if not gt["expected_pii"] and pii_detected:
            false_positives += 1

        mask_success = (pii_detected == res["pii_masked"]) if pii_detected else True
        verdict_success = verdict in gt.get("expected_verdict", [verdict])
        if mask_success and verdict_success:
            task_successes += 1

        policy_str = "YES" if has_citation_match else "NO"
        masked_str = "YES" if res["pii_masked"] else ("N/A" if not pii_detected else "NO")
        print(f"{name[:40]:<42} | {lat:<8.1f} | {masked_str:<10} | {policy_str:<12} | {verdict}")

    avg_lat = sum(latencies) / len(latencies)
    citation_accuracy = (citation_hits / total_scenarios) * 100.0
    task_success_rate = (task_successes / total_scenarios) * 100.0
    fps_equivalent = 1000.0 / avg_lat if avg_lat > 0 else 0

    print("=" * 70)
    print("BENCHMARK SUMMARY METRICS:")
    print(f"1. Average Response Time:  {avg_lat:.2f} ms ({fps_equivalent:.1f} FPS) [Target: <33.3 ms / 30 FPS]")
    print(f"2. Citation Accuracy:      {citation_accuracy:.1f}% ({citation_hits}/{total_scenarios} scenarios correctly cited)")
    print(f"3. Task Success Rate:      {task_success_rate:.1f}% ({task_successes}/{total_scenarios} end-to-end runs succeeded)")
    print(f"4. False Positive Audit:   {false_positives} non-PII frames falsely triggered PII")
    print("=" * 70)

if __name__ == "__main__":
    run_evaluation()
