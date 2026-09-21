"""
GlassShield: Human-AI Co-Design Streamlit Application
Milestone: CS 5542 Challenge 2
Task: Sensor/Privacy Layer PII Blurring, Grounded Policy RAG, and Human Verification Gate
"""

import json
import os
import time
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

# Import GlassShield core modules
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

# Page configuration
st.set_page_config(
    page_title="GlassShield: Human-AI Privacy Co-Design",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize singletons in session state
@st.cache_resource
def get_privacy_engine() -> PrivacyEngine:
    return PrivacyEngine(
        face_model_path="models/ego_blur_face_gen1.jit",
        lp_model_path="models/ego_blur_lp_gen1.jit",
    )

@st.cache_resource
def get_policy_rag() -> PolicyRAG:
    return PolicyRAG()

@st.cache_resource
def get_sample_loader() -> Dict[str, str]:
    return SampleDataLoader.ensure_samples()

if "telemetry_store" not in st.session_state:
    st.session_state.telemetry_store = TelemetryStore()

if "manual_boxes" not in st.session_state:
    st.session_state.manual_boxes = []

if "session_reviews" not in st.session_state:
    st.session_state.session_reviews = []

# Header
st.title("🛡️ GlassShield: Human–AI Co-Design")
st.caption(
    "**CS 5542 Challenge 2 First P1 Task** • On-Device Egocentric PII Filtering (EgoBlur) + "
    "Regulatory Policy RAG + Human Verification Gate"
)

engine = get_privacy_engine()
rag = get_policy_rag()
samples = get_sample_loader()
explainer = AIExplainer()

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.header("⚙️ Interaction & Controls")

    # 1. Media Input Selection
    input_mode = st.radio(
        "Select Input Source",
        ["Curated Benchmark Sample", "Upload Custom Frame"],
        index=0,
    )

    image_source = None
    source_name = "test_frame"

    if input_mode == "Curated Benchmark Sample":
        scenario_choice = st.selectbox("Egocentric Scenario", list(samples.keys()))
        source_name = scenario_choice
        sample_path = samples[scenario_choice]
        if os.path.exists(sample_path):
            image_source = Image.open(sample_path)
    else:
        uploaded_file = st.file_uploader(
            "Upload Egocentric Image (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
        )
        if uploaded_file is not None:
            image_source = Image.open(uploaded_file)
            source_name = uploaded_file.name

    st.markdown("---")
    st.subheader("🔍 Search & Regulatory Filter")
    user_query = st.text_input(
        "Search Policy or Telemetry (e.g. 'bystander consent', 'GDPR', 'vehicle')",
        value="",
        placeholder="Type keyword or query...",
    )

    st.markdown("---")
    st.subheader("🎛️ Detection Filters")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        detect_faces = st.checkbox("Detect Faces", value=True)
    with col_t2:
        detect_plates = st.checkbox("Detect Plates", value=True)

    score_thresh = st.slider("Confidence Threshold", 0.10, 0.95, 0.35, 0.05)
    nms_thresh = st.slider("NMS IoU Threshold", 0.10, 0.90, 0.50, 0.05)

    st.markdown("---")
    st.subheader("🎨 Privacy Obfuscation")
    blur_style = st.selectbox(
        "Obfuscation Method",
        ["gaussian_blur", "solid_mask", "pixelate"],
        index=0,
        format_func=lambda x: {
            "gaussian_blur": "Gaussian Blur",
            "solid_mask": "Solid Privacy Mask",
            "pixelate": "Pixelate / Mosaic",
        }[x],
    )
    blur_intensity = st.slider("Blur Kernel / Intensity", 15, 99, 51, 6)

    st.markdown("---")
    if st.button("🔄 Clear Manual Boxes & Reset Reviews"):
        st.session_state.manual_boxes = []
        st.session_state.session_reviews = []
        st.rerun()

# ----------------- MAIN PROCESSING -----------------
if image_source is None:
    st.info("👈 Please select a benchmark scenario or upload an egocentric frame from the sidebar.")
    st.stop()

# Run Privacy Engine
with st.spinner("Executing on-device EgoBlur inference..."):
    results = engine.process_frame(
        image_input=image_source,
        detect_faces=detect_faces,
        detect_plates=detect_plates,
        score_threshold=score_thresh,
        nms_iou_threshold=nms_thresh,
        blur_style=blur_style,
        blur_intensity=blur_intensity,
        manual_boxes=st.session_state.manual_boxes,
    )

# Run Policy RAG
detected_class_names = [e["class_name"] for e in results["detected_entities"]]
min_conf = min([e["confidence"] for e in results["detected_entities"]]) if results["detected_entities"] else 1.0
retrieved_policies = rag.retrieve(
    query=user_query,
    detected_classes=detected_class_names,
    min_confidence=min_conf,
    top_k=3,
)

# Run AI Explainer
explanation = explainer.generate_explanation(
    detected_entities=results["detected_entities"],
    retrieved_policies=retrieved_policies,
    filter_latency_ms=results["filter_latency_ms"],
    context_description=source_name,
)

# Build Telemetry Tuple
current_event = TelemetryTuple(
    sensor_trigger=SensorTrigger(source="camera", trigger_type="continuous_stream"),
    privacy_layer=PrivacyLayerTelemetry(
        faces_detected=results["faces_detected"],
        plates_detected=results["plates_detected"],
        pii_masked=results["pii_masked"],
        filter_latency_ms=results["filter_latency_ms"],
    ),
    network_flow=NetworkFlowTelemetry(
        sni_domain="edge.glassshield.internal",
        flow_classification="normal" if results["pii_masked"] or not results["detected_entities"] else "abnormal_leak",
    ),
    vlm_agent=VlmAgentTelemetry(
        model_id="EgoBlur-Gen1-TorchScript",
        prompt_digest=f"sha256-{hash(source_name) & 0xffffffff:08x}",
    ),
    action_gate=ActionGateTelemetry(
        verification_verdict=explanation["recommended_verdict"],
        reasoning=explanation["gate_reasoning"],
    ),
)

# ----------------- TOP METRIC BAR -----------------
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    fps_rate = 1000.0 / results["filter_latency_ms"] if results["filter_latency_ms"] > 0 else 0
    st.metric(
        "Processing Latency",
        f"{results['filter_latency_ms']:.1f} ms",
        delta=f"{33.0 - results['filter_latency_ms']:.1f} ms vs 30FPS Target",
        delta_color="normal" if results["filter_latency_ms"] < 33.0 else "inverse",
    )
with m_col2:
    total_pii = len(results["detected_entities"])
    st.metric("Total Visual PII", f"{total_pii} Entities", f"Faces: {results['faces_detected']} | Plates: {results['plates_detected']}")
with m_col3:
    verdict = explanation["recommended_verdict"]
    color = "🟢" if verdict == "ALLOW" else ("🟠" if verdict == "USER_CONFIRMATION_REQUIRED" else "🔴")
    st.metric("AI Gate Recommendation", f"{color} {verdict}")
with m_col4:
    uncertainty_pct = explanation["uncertainty_score"] * 100
    st.metric("Uncertainty Score", f"{uncertainty_pct:.0f}%", delta="Low Risk" if uncertainty_pct < 30 else "Requires Review", delta_color="inverse")

# ----------------- TABS WORKFLOW -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Visual Evidence & Side-by-Side Review",
    "🧠 Grounded AI Explanation & Policy RAG",
    "📋 Detection Inventory & Telemetry Contract",
    "🤝 Human Review, Refinement & FPR Benchmark",
])

# TAB 1: Visual Evidence
with tab1:
    st.subheader("Visual Evidence Verification")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.markdown("**Original Frame + EgoBlur Bounding Boxes**")
        st.image(results["overlay_image"], use_container_width=True)
        st.caption("Boxes in orange = Bystander Face, Cyan = License Plate.")

    with col_img2:
        st.markdown(f"**Anonymized Privacy Stream ({blur_style})**")
        st.image(results["anonymized_image"], use_container_width=True)
        st.caption("Rendered on-device before any network dispatch or cloud persistence.")

    st.markdown("### 🏷️ Provenance & Device Verification")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.text(f"Device Target: {results['device'].upper()}")
    with p_col2:
        st.text(f"Resolution: {results['image_dimensions']['width']}x{results['image_dimensions']['height']}")
    with p_col3:
        st.text(f"Model: EgoBlur Gen1 JIT")
    with p_col4:
        st.text(f"Event ID: {current_event.event_id[:8]}...")

# TAB 2: Grounded AI Explanation & Policy RAG
with tab2:
    st.subheader("Grounded Regulatory & Privacy Explanation")
    st.markdown(explanation["narrative"])

    st.markdown("---")
    st.subheader("📚 Retrieved Policy Evidence (RAG Corpus)")
    if not retrieved_policies:
        st.warning("No regulatory policies matched current context or search query.")
    else:
        for idx, pol in enumerate(retrieved_policies, 1):
            with st.expander(
                f"#{idx}: [{pol['id']}] {pol['title']} (Relevance: {pol['relevance_score'] * 100:.0f}%)",
                expanded=(idx == 1),
            ):
                st.markdown(f"**Jurisdiction**: `{pol['jurisdiction']}` | **Category**: `{pol['category']}` | **Risk Level**: `{pol['risk_level']}`")
                st.markdown(f"**Summary**: {pol['summary']}")
                st.markdown(f"**Exact Rule Citation**: *\"{pol['rule_text']}\"*")
                st.markdown(f"**Recommended Action**: `{pol['recommended_action']}` | **Default Gate Verdict**: `{pol['default_gate_verdict']}`")

# TAB 3: Detection Inventory & Telemetry Contract
with tab3:
    st.subheader("Detection Entity Inventory")
    if not results["detected_entities"]:
        st.info("No PII detected in this frame.")
    else:
        df_entities = pd.DataFrame([
            {
                "ID": e["entity_id"],
                "Class": e["class_name"],
                "Confidence": f"{e['confidence'] * 100:.1f}%",
                "Bounding Box [x1, y1, x2, y2]": str(e["box"]),
                "Frame Area %": f"{e['area_pct']}%",
                "Source": e["detection_source"],
                "Status": "Masked",
            }
            for e in results["detected_entities"]
        ])
        st.dataframe(df_entities, use_container_width=True)

    st.markdown("---")
    st.subheader("📄 Standardized Cross-Layer Telemetry Tuple")
    st.caption("Conforms strictly to the `TelemetryTuple` contract in `memory.md`.")
    st.json(current_event.to_dict())

    st.download_button(
        "💾 Export Telemetry Event JSON",
        data=current_event.to_json(indent=2),
        file_name=f"telemetry_event_{current_event.event_id[:8]}.json",
        mime="application/json",
    )

# TAB 4: Human Review, Refinement & FPR Benchmark
with tab4:
    st.subheader("Human Review & Feedback Gate")
    st.write(
        "The human remains in control. Review the AI's proposal, correct misdetections, "
        "or refine bounding boxes to uphold safety and regulatory accountability."
    )

    h_col1, h_col2 = st.columns(2)
    with h_col1:
        st.markdown("#### 1. Action Gate Verdict Override")
        selected_gate_override = st.selectbox(
            "Verdict Decision",
            ["ALLOW", "BLOCK", "USER_CONFIRMATION_REQUIRED"],
            index=["ALLOW", "BLOCK", "USER_CONFIRMATION_REQUIRED"].index(explanation["recommended_verdict"]),
        )
        human_notes = st.text_area(
            "Auditor / Wearer Review Notes",
            value="",
            placeholder="Document rationale (e.g. 'Confirmed bystander anonymization', 'Overrode false positive on statue')...",
        )

    with h_col2:
        st.markdown("#### 2. Detection Quality Audit")
        audit_classification = st.radio(
            "Classify Detection Result",
            [
                "Correct (True Positive / True Negative)",
                "False Positive (Flag Non-PII Box)",
                "False Negative (Missed PII)",
            ],
            index=0,
        )

        st.markdown("#### 3. Manual Bounding Box Refinement (Add Missing Box)")
        with st.expander("➕ Add Missing Box Coordinates"):
            c_x1, c_y1 = st.columns(2)
            with c_x1:
                man_x1 = st.number_input("X1", value=0, min_value=0, max_value=results["image_dimensions"]["width"])
                man_y1 = st.number_input("Y1", value=0, min_value=0, max_value=results["image_dimensions"]["height"])
            with c_y1:
                man_x2 = st.number_input("X2", value=100, min_value=0, max_value=results["image_dimensions"]["width"])
                man_y2 = st.number_input("Y2", value=100, min_value=0, max_value=results["image_dimensions"]["height"])

            if st.button("Add Box to Masking List"):
                if man_x2 > man_x1 and man_y2 > man_y1:
                    st.session_state.manual_boxes.append([man_x1, man_y1, man_x2, man_y2])
                    st.success(f"Added manual box [{man_x1}, {man_y1}, {man_x2}, {man_y2}]. Re-running...")
                    st.rerun()
                else:
                    st.error("Invalid coordinates: X2 must be > X1 and Y2 must be > Y1.")

    if st.button("✅ Submit Human Review & Log Event"):
        status_map = {
            "Correct (True Positive / True Negative)": "APPROVED",
            "False Positive (Flag Non-PII Box)": "CORRECTED_FP",
            "False Negative (Missed PII)": "CORRECTED_FN",
        }
        review_status = status_map[audit_classification]
        current_event.human_review_status = review_status
        current_event.human_notes = human_notes
        current_event.action_gate.verification_verdict = selected_gate_override

        st.session_state.telemetry_store.log(current_event)
        st.session_state.session_reviews.append({
            "timestamp": current_event.timestamp,
            "scenario": source_name,
            "verdict": selected_gate_override,
            "audit_status": review_status,
            "notes": human_notes,
            "latency_ms": results["filter_latency_ms"],
        })
        st.success(f"Event {current_event.event_id[:8]} logged with status '{review_status}' and verdict '{selected_gate_override}'!")
        st.rerun()

    st.markdown("---")
    st.subheader("📊 Session Benchmark & FPR Ledger")
    metrics = st.session_state.telemetry_store.get_metrics_summary()

    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.metric("Logged Events", metrics["total_events"])
    with b_col2:
        st.metric("Avg Latency", f"{metrics['mean_latency_ms']} ms")
    with b_col3:
        st.metric("Flagged False Positives", metrics["flagged_false_positives"])
    with b_col4:
        st.metric(
            "False Positive Rate (FPR)",
            f"{metrics['false_positive_rate']}%",
            delta="Target < 5.0%",
            delta_color="normal" if metrics["false_positive_rate"] < 5.0 else "inverse",
        )

    if st.session_state.session_reviews:
        st.markdown("**Review Audit History**")
        st.dataframe(pd.DataFrame(st.session_state.session_reviews), use_container_width=True)

        # Latency chart
        df_chart = pd.DataFrame(st.session_state.session_reviews)
        st.markdown("**Latency Performance by Scenario (Target: < 33 ms)**")
        st.bar_chart(df_chart.set_index("scenario")["latency_ms"])
