"""
GlassShield: Network-Aware Security & Privacy for AI Smart Glasses
End-to-End Human-AI Workflow:
Human Input -> Data/Tools/Retrieval/AI -> Result + Evidence -> Human Review
Implements:
1. Encrypted wireless metadata meta-activity inference (Signal-to-Event pipeline)
2. Defensible reasoning contract: observable events vs. subjective intent
3. Calibrated uncertainty & open-set abstention (UNKNOWN class)
4. Citation-strict, grounded Policy RAG with section-level audit trail
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
from layer_03_network_anomalies.meta_activity_engine import MetaActivityEngine, PacketMetadata
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
    page_title="GlassShield: Network-Aware Security & Privacy",
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
def get_meta_engine() -> MetaActivityEngine:
    return MetaActivityEngine()

@st.cache_resource
def get_policy_rag() -> PolicyRAG:
    return PolicyRAG()

@st.cache_resource
def get_sample_loader() -> Dict[str, str]:
    return SampleDataLoader.ensure_samples()

if "telemetry_store" not in st.session_state:
    st.session_state.telemetry_store = TelemetryStore()

if "session_reviews" not in st.session_state:
    st.session_state.session_reviews = []

if "manual_boxes" not in st.session_state:
    st.session_state.manual_boxes = []

engine = get_privacy_engine()
meta_engine = get_meta_engine()
rag = get_policy_rag()
samples = get_sample_loader()
explainer = AIExplainer()

# ----------------- HEADER -----------------
st.title("🛡️ GlassShield: Network-Aware Security & Privacy")
st.caption(
    "**Core Scientific Mission**: Privacy-preserving smart-glasses meta-activity inference from encrypted "
    "wireless metadata + Multimodal presence fusion + Citation-grounded policy reasoning + Human Action Gate."
)

# ----------------- SIDEBAR CONTROLS (HUMAN INPUT) -----------------
with st.sidebar:
    st.header("⚙️ Human Input & Controls")

    # Workflow Modality
    pipeline_mode = st.radio(
        "Primary Workflow Pipeline",
        [
            "📡 Encrypted Traffic Meta-Activity & Policy RAG",
            "📸 Egocentric Visual Privacy & EgoBlur Engine",
        ],
        index=0,
    )

    st.markdown("---")

    if pipeline_mode == "📡 Encrypted Traffic Meta-Activity & Policy RAG":
        st.subheader("1. Encrypted Traffic Scenario")
        scenario_choice = st.selectbox(
            "Select Authorized Wireless Trace",
            [
                "Exam Session: Camera Burst + Cloud LLM Query",
                "Cleanroom R&D: Continuous Video Stream",
                "Library Study: Benign Wear & Periodic Cloud Sync",
                "Adversarial Jitter: Ambiguous Low-Confidence Stream",
            ],
            index=0,
        )

        st.markdown("---")
        st.subheader("2. Policy Query & Constraints")
        user_policy_query = st.text_input(
            "Refine Legal/Policy Search Query",
            value="",
            placeholder="e.g. 'exam proctoring', 'cleanroom', 'cloud sync'...",
        )

        st.markdown("---")
        st.subheader("3. Reliability & Abstention Filters")
        abstention_threshold = st.slider(
            "Open-Set Abstention Threshold",
            min_value=0.40,
            max_value=0.95,
            value=0.65,
            step=0.05,
            help="If maximum activity probability is below this threshold, GlassShield abstains with 'UNKNOWN' to prevent false accusations.",
        )

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            window_size_s = st.slider("Window (s)", 0.5, 3.0, 1.0, 0.5)
        with col_w2:
            step_size_s = st.slider("Step (s)", 0.5, 2.0, 1.0, 0.5)

        st.markdown("---")
        st.subheader("4. Multimodal Optical Modality")
        optical_enabled = st.checkbox("Enable Optical Presence Sensor", value=True)
        optical_detected = st.checkbox("Waveguide Specular Signature Detected", value=True) if optical_enabled else False
        st.caption("Non-content optical evidence (Ye et al., HotMobile 2026). No visual scene frames are captured.")

    else:
        st.subheader("1. Egocentric Visual Input")
        visual_scenario = st.selectbox("Benchmark Frame", list(samples.keys()))
        sample_path = samples[visual_scenario]
        image_source = Image.open(sample_path) if os.path.exists(sample_path) else None

        st.markdown("---")
        st.subheader("2. Visual Privacy Filters")
        detect_faces = st.checkbox("Detect Bystander Faces", value=True)
        detect_plates = st.checkbox("Detect License Plates", value=True)
        score_thresh = st.slider("Detector Confidence Threshold", 0.10, 0.95, 0.35, 0.05)
        nms_thresh = st.slider("NMS IoU Threshold", 0.10, 0.90, 0.50, 0.05)
        blur_style = st.selectbox("Obfuscation Style", ["gaussian_blur", "solid_mask", "pixelate"], index=0)
        blur_intensity = st.slider("Blur Intensity", 15, 99, 51, 6)

    st.markdown("---")
    if st.button("🔄 Reset Session Reviews & Telemetry"):
        st.session_state.session_reviews = []
        st.session_state.manual_boxes = []
        st.rerun()


# ==============================================================================
# PIPELINE 1: ENCRYPTED TRAFFIC META-ACTIVITY & POLICY RAG (CORE WORKFLOW)
# ==============================================================================
if pipeline_mode == "📡 Encrypted Traffic Meta-Activity & Policy RAG":

    # --- 1. DATA / TOOLS: Generate & Classify Packet Flow ---
    start_time = time.perf_counter()
    raw_packets = meta_engine.generate_benchmark_trace(scenario_choice)
    analysis_res = meta_engine.analyze_stream(
        packets=raw_packets,
        window_size_s=window_size_s,
        step_size_s=step_size_s,
        abstention_threshold=abstention_threshold,
        optical_presence_enabled=optical_enabled,
        optical_presence_detected=optical_detected,
    )
    inference_latency_ms = (time.perf_counter() - start_time) * 1000.0

    # --- 2. RETRIEVAL: Grounded Policy RAG ---
    inferred_events = [e.activity for e in analysis_res["events"]]
    retrieved_policies = rag.retrieve(
        query=user_policy_query,
        event_sequence=inferred_events,
        top_k=3,
    )

    # --- 3. AI REASONER: Defensible Explanation Contract ---
    explanation = explainer.generate_network_meta_explanation(
        event_timeline_str=analysis_res["timeline_str"],
        events=analysis_res["events"],
        retrieved_policies=retrieved_policies,
        optical_presence=analysis_res["optical_presence"],
        mean_uncertainty=analysis_res["mean_uncertainty"],
        abstention_count=analysis_res["abstention_count"],
    )

    # --- 4. BUILD CROSS-LAYER TELEMETRY CONTRACT ---
    current_event = TelemetryTuple(
        sensor_trigger=SensorTrigger(source="companion_sync", trigger_type="user_invoked"),
        privacy_layer=PrivacyLayerTelemetry(
            faces_detected=0,
            plates_detected=0,
            pii_masked=True,
            filter_latency_ms=inference_latency_ms,
        ),
        network_flow=NetworkFlowTelemetry(
            sni_domain="edge.glassshield.internal",
            packet_count=len(raw_packets),
            flow_classification="abnormal_leak" if explanation["recommended_verdict"] == "BLOCK" else "normal",
            classifier_confidence=round(1.0 - analysis_res["mean_uncertainty"], 3),
            inferred_activity_sequence=inferred_events,
            optical_presence_detected=analysis_res["optical_presence"]["detected"],
            optical_confidence=analysis_res["optical_presence"]["confidence"],
            abstention_triggered=analysis_res["abstention_count"] > 0,
            calibrated_uncertainty=analysis_res["mean_uncertainty"],
        ),
        vlm_agent=VlmAgentTelemetry(model_id="Meta-Activity-RF-Transformer-Ensemble"),
        action_gate=ActionGateTelemetry(
            verification_verdict=explanation["recommended_verdict"],
            reasoning=explanation["gate_reasoning"],
        ),
    )

    # --- TOP METRIC BANNER ---
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(
            "Signal Pipeline Latency",
            f"{inference_latency_ms:.1f} ms",
            delta=f"{len(raw_packets)} encrypted packets parsed",
            delta_color="normal",
        )
    with col_m2:
        top_activity = analysis_res["events"][1].activity if len(analysis_res["events"]) > 1 else analysis_res["events"][0].activity if analysis_res["events"] else "NONE"
        st.metric(
            "Primary Meta-Activity",
            top_activity,
            f"{len(analysis_res['events'])} sequence events",
        )
    with col_m3:
        unc_val = analysis_res["mean_uncertainty"] * 100
        is_high_unc = unc_val > 35.0
        st.metric(
            "Calibrated Uncertainty",
            f"{unc_val:.1f}%",
            delta=f"{analysis_res['abstention_count']} Abstentions" if analysis_res['abstention_count'] > 0 else "High Confidence",
            delta_color="inverse" if is_high_unc else "normal",
        )
    with col_m4:
        verd = explanation["recommended_verdict"]
        badge = "🟢" if verd == "ALLOW" else ("🟠" if verd == "USER_CONFIRMATION_REQUIRED" else "🔴")
        st.metric("Action Gate Recommendation", f"{badge} {verd}")

    # --- TABS WORKFLOW (RESULT + EVIDENCE + HUMAN REVIEW) ---
    tab_signal, tab_rag, tab_compare, tab_review = st.tabs([
        "📊 Network Evidence & Event Waterfall",
        "🧠 Policy RAG & Defensible Reasoning",
        "⚖️ Compare Alternatives & Probabilities",
        "🤝 Human Review & Action Gate",
    ])

    # TAB 1: Network Evidence & Event Waterfall
    with tab_signal:
        st.subheader("📡 Encrypted Wireless Packet Metadata (No Payload Decryption)")
        st.caption(
            "Observations strictly limited to timing, size, direction, and burst cadence. "
            "Zero application payloads or visual camera frames are accessed or decrypted."
        )

        df_packets = pd.DataFrame([
            {
                "Time (s)": p.timestamp_s,
                "Packet Size (Bytes)": p.length_bytes,
                "Direction": p.direction,
                "Signed Length": p.signed_length,
                "Protocol": p.protocol,
                "Delta t (ms)": p.delta_t_ms,
            }
            for p in raw_packets
        ])

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("**Packet Sizes Over Time (Signed Length: Uplink > 0, Downlink < 0)**")
            st.line_chart(df_packets.set_index("Time (s)")["Signed Length"])
        with col_c2:
            st.markdown("**Inter-Packet Arrival Time Distribution (IAT ms)**")
            st.bar_chart(df_packets.set_index("Time (s)")["Delta t (ms)"])

        st.markdown("---")
        st.subheader("⏱️ Temporal Fusion: Operational Meta-Activity Sequence")
        st.info(f"**Chronological Event Timeline**: `{analysis_res['timeline_str']}`")

        df_events = pd.DataFrame([
            {
                "Order": e.event_order,
                "Operational Activity": e.activity,
                "Start Time": f"T+{e.start_time_s}s",
                "End Time": f"T+{e.end_time_s}s",
                "Duration": f"{e.duration_s}s",
                "Confidence": f"{e.mean_confidence * 100:.1f}%",
                "Status": e.status,
                "Evidence Notes": e.notes,
            }
            for e in analysis_res["events"]
        ])
        st.dataframe(df_events, use_container_width=True)

        if analysis_res["abstention_count"] > 0:
            st.warning(
                f"⚠️ **Open-Set Abstention Engaged ({analysis_res['abstention_count']} segments)**: "
                f"Portions of this traffic stream fell below the {abstention_threshold * 100:.0f}% confidence boundary. "
                "The system abstained with `UNKNOWN` to avoid falsely categorizing benign or shifted traffic."
            )

    # TAB 2: Grounded Policy RAG & Defensible Reasoning
    with tab_rag:
        st.subheader("🧠 Downstream Policy Grounding & Interpretation")
        st.markdown(explanation["narrative"])

        st.markdown("---")
        st.subheader("📚 Retrieved Policy Passages (Section-Level Authority)")
        if not retrieved_policies:
            st.warning("No policies matched the current event timeline or user query.")
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

        st.markdown("---")
        st.subheader("📄 Standardized Cross-Layer Telemetry Tuple")
        st.json(current_event.to_dict())

    # TAB 3: Compare Alternatives & Probabilities
    with tab_compare:
        st.subheader("⚖️ Compare Alternative Meta-Activity Hypotheses")
        st.write(
            "Inspect the calibrated probability distribution across competing hypotheses "
            "(e.g., distinguishing interactive AI assistance from non-interactive background sync)."
        )

        if analysis_res["window_predictions"]:
            window_options = [
                f"Window {p.window_id} ({p.start_time_s:.1f}s - {p.end_time_s:.1f}s) -> Inferred: {p.predicted_activity} ({p.confidence * 100:.0f}%)"
                for p in analysis_res["window_predictions"]
            ]
            selected_win_str = st.selectbox("Select Window to Inspect", window_options)
            sel_idx = int(selected_win_str.split()[1])
            selected_win = analysis_res["window_predictions"][sel_idx]

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f"**Probabilities for Window {selected_win.window_id}**")
                df_probs = pd.DataFrame(
                    list(selected_win.probabilities.items()),
                    columns=["Operational Activity", "Calibrated Probability"],
                ).set_index("Operational Activity")
                st.bar_chart(df_probs)

            with col_p2:
                st.markdown("**Window Physical Flow Features**")
                feats = selected_win.features
                st.json({
                    "packet_count": feats.packet_count,
                    "total_bytes": feats.total_bytes,
                    "uplink_ratio": feats.uplink_ratio,
                    "mean_packet_size_bytes": feats.mean_packet_size,
                    "mean_inter_packet_time_ms": feats.mean_iat_ms,
                    "burst_rate_kbps": feats.burst_rate_kbps,
                    "calibrated_uncertainty": selected_win.uncertainty_score,
                    "is_abstained": selected_win.is_abstained,
                })

    # TAB 4: Human Review & Action Gate
    with tab_review:
        st.subheader("🤝 Human Review, Refinement & Action Gate")
        st.write(
            "The human reviewer inspects the evidence, resolves ambiguities, corrects the AI, "
            "and makes the authoritative determination."
        )

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("#### 1. Action Gate Verdict Override")
            gate_decision = st.selectbox(
                "Final Human Verdict",
                ["ALLOW", "BLOCK", "USER_CONFIRMATION_REQUIRED"],
                index=["ALLOW", "BLOCK", "USER_CONFIRMATION_REQUIRED"].index(explanation["recommended_verdict"]),
            )
            reviewer_rationale = st.text_area(
                "Document Rationale / Justification",
                value="",
                placeholder="e.g. 'Confirmed prohibited exam AI interaction pattern', 'Overrode false alarm; verified authorized sync'...",
            )

        with col_h2:
            st.markdown("#### 2. Classifier Quality Audit")
            audit_verdict = st.radio(
                "Audit Finding",
                [
                    "Correct (True Positive / True Negative)",
                    "False Positive (Benign traffic flagged as restricted)",
                    "False Negative (Restricted activity missed)",
                    "Appropriate Abstention (Uncertainty correctly flagged)",
                ],
                index=0,
            )

            st.markdown("#### 3. Quick Action Buttons")
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                accept_clicked = st.button("✅ Accept AI Verdict", use_container_width=True)
            with b_col2:
                block_clicked = st.button("🚫 Force BLOCK", use_container_width=True)
            with b_col3:
                allow_clicked = st.button("🟢 Force ALLOW", use_container_width=True)

        if accept_clicked or block_clicked or allow_clicked or st.button("💾 Submit Formal Human Review"):
            final_v = gate_decision
            if block_clicked:
                final_v = "BLOCK"
            elif allow_clicked:
                final_v = "ALLOW"

            status_mapping = {
                "Correct (True Positive / True Negative)": "APPROVED",
                "False Positive (Benign traffic flagged as restricted)": "CORRECTED_FP",
                "False Negative (Restricted activity missed)": "CORRECTED_FN",
                "Appropriate Abstention (Uncertainty correctly flagged)": "APPROVED_ABSTENTION",
            }
            rev_status = status_mapping[audit_verdict]

            current_event.human_review_status = rev_status
            current_event.human_notes = reviewer_rationale
            current_event.action_gate.verification_verdict = final_v

            st.session_state.telemetry_store.log(current_event)
            st.session_state.session_reviews.append({
                "timestamp": current_event.timestamp,
                "scenario": scenario_choice,
                "verdict": final_v,
                "audit_status": rev_status,
                "uncertainty": f"{analysis_res['mean_uncertainty'] * 100:.1f}%",
                "notes": reviewer_rationale,
                "latency_ms": round(inference_latency_ms, 1),
            })
            st.success(f"Review recorded! Event {current_event.event_id[:8]} committed with verdict '{final_v}'.")
            st.rerun()

        # Session Benchmark Ledger
        st.markdown("---")
        st.subheader("📊 Session Benchmark & Reliability Ledger")
        if st.session_state.session_reviews:
            df_revs = pd.DataFrame(st.session_state.session_reviews)
            st.dataframe(df_revs, use_container_width=True)

            m_col1, m_col2, m_col3 = st.columns(3)
            fp_count = sum(1 for r in st.session_state.session_reviews if r["audit_status"] == "CORRECTED_FP")
            total_revs = len(st.session_state.session_reviews)
            fpr = (fp_count / total_revs * 100.0) if total_revs > 0 else 0.0

            with m_col1:
                st.metric("Total Reviews Logged", total_revs)
            with m_col2:
                st.metric("False Positive Interventions", fp_count)
            with m_col3:
                st.metric("Empirical FPR", f"{fpr:.1f}%", delta="Target < 5.0%", delta_color="normal" if fpr < 5.0 else "inverse")
        else:
            st.info("No reviews committed yet in this session. Use the controls above to log reviews.")


# ==============================================================================
# PIPELINE 2: EGOCENTRIC VISUAL PRIVACY & EGOBLUR ENGINE (VISION SLICE)
# ==============================================================================
else:
    if image_source is None:
        st.info("👈 Please select a benchmark scenario or upload a frame from the sidebar.")
        st.stop()

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

    detected_class_names = [e["class_name"] for e in results["detected_entities"]]
    min_conf = min([e["confidence"] for e in results["detected_entities"]]) if results["detected_entities"] else 1.0
    retrieved_policies = rag.retrieve(
        detected_classes=detected_class_names,
        min_confidence=min_conf,
        top_k=3,
    )

    explanation = explainer.generate_explanation(
        detected_entities=results["detected_entities"],
        retrieved_policies=retrieved_policies,
        filter_latency_ms=results["filter_latency_ms"],
        context_description=visual_scenario,
    )

    # Build Visual Telemetry Contract
    current_visual_event = TelemetryTuple(
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
            prompt_digest=f"sha256-{hash(visual_scenario) & 0xffffffff:08x}",
        ),
        action_gate=ActionGateTelemetry(
            verification_verdict=explanation["recommended_verdict"],
            reasoning=explanation["gate_reasoning"],
        ),
    )

    # 4 Dynamic Tabs for Visual Privacy
    v_tab1, v_tab2, v_tab3, v_tab4 = st.tabs([
        "📸 Visual Evidence & Side-by-Side Review",
        "🧠 Grounded AI Explanation & Policy RAG",
        "📋 Detection Inventory & Telemetry Contract",
        "🤝 Human Review, Refinement & FPR Benchmark",
    ])

    # TAB 1: Visual Evidence
    with v_tab1:
        st.subheader("Visual Evidence Verification")
        c_img1, c_img2 = st.columns(2)
        with c_img1:
            st.markdown("**Original Egocentric Frame + EgoBlur Bounding Boxes**")
            st.image(results["overlay_image"], use_container_width=True)
            st.caption("Orange boxes = Bystander Face, Blue/Cyan = License Plate.")

        with c_img2:
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
            st.text(f"Event ID: {current_visual_event.event_id[:8]}...")

    # TAB 2: Grounded AI Explanation & Policy RAG
    with v_tab2:
        st.subheader("Grounded Regulatory & Privacy Explanation")
        st.markdown(explanation["narrative"])

        st.markdown("---")
        st.subheader("📚 Retrieved Policy Evidence (RAG Corpus)")
        if not retrieved_policies:
            st.warning("No regulatory policies matched current context.")
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
    with v_tab3:
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
        st.caption("Conforms strictly to the `TelemetryTuple` contract.")
        st.json(current_visual_event.to_dict())

        st.download_button(
            "💾 Export Telemetry Event JSON",
            data=current_visual_event.to_json(indent=2),
            file_name=f"telemetry_event_{current_visual_event.event_id[:8]}.json",
            mime="application/json",
        )

    # TAB 4: Human Review, Refinement & FPR Benchmark
    with v_tab4:
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
            current_visual_event.human_review_status = review_status
            current_visual_event.human_notes = human_notes
            current_visual_event.action_gate.verification_verdict = selected_gate_override

            st.session_state.telemetry_store.log(current_visual_event)
            st.session_state.session_reviews.append({
                "timestamp": current_visual_event.timestamp,
                "scenario": visual_scenario,
                "verdict": selected_gate_override,
                "audit_status": review_status,
                "notes": human_notes,
                "latency_ms": results["filter_latency_ms"],
            })
            st.success(f"Event {current_visual_event.event_id[:8]} logged with status '{review_status}' and verdict '{selected_gate_override}'!")
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

