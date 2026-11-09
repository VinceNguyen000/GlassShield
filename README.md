# GlassShield 🛡️🕶️
**Network-Aware Security and Privacy for AI Smart Glasses**  
*From Edge Sensors & Companion Apps to Graph Machine Learning, Cloud Agents, and Human Review*

[![Course](https://img.shields.io/badge/Course-CS_5542_Big_Data_Analytics-blue.svg)](#)
[![Instructor](https://img.shields.io/badge/Instructor-Dr._Yugyung_Lee-darkblue.svg)](#)
[![Hack-A-Roo](https://img.shields.io/badge/Hack--A--Roo-2026_Finalist-gold.svg)](#)
[![Status](https://img.shields.io/badge/Status-Complete_Challenge_5-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-red.svg)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-TorchScript_JIT-orange.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-13%2F13_Passing-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

---

## 🏛️ Course & Team Metadata
* **Course**: CS 5542 — Big Data Analytics & Applications (Fall 2026)
* **Instructor**: Dr. Yugyung Lee
* **Institution**: University of Missouri-Kansas City (UMKC) — School of Science & Engineering
* **Author / Team Member**: Vien (Vince) Nguyen
* **Repository**: [https://github.com/VinceNguyen000/GlassShield](https://github.com/VinceNguyen000/GlassShield)
* **Competition**: Hack-A-Roo 2026

---


## 📖 Executive Summary & Core Philosophy

**GlassShield** is an evidence-driven Human–AI Co-Design defense system for commercial AI smart glasses (such as Meta Ray-Ban and Project Aria). Smart glasses continuously capture first-person (egocentric) audio-visual streams and transmit telemetry over encrypted Wi-Fi/cellular links. While enabling hands-free AI assistance, they trigger a severe operational crisis spanning user cognitive safety, bystander privacy, and enterprise security.

GlassShield operates on a foundational scientific philosophy:
> *"Tools calculate. RAG retrieves. LLMs interpret. Humans review and control."*

Rather than relying on opaque end-to-end neural models or hallucination-prone chatbots, GlassShield enforces strict separation of concerns across a 6-layer decoupled defense pipeline.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       GLASSSHIELD DUAL PIPELINE                                  │
├──────────────────────────────────────────────────────────────────┬───────────────────────────────┤
│ 📸 Pipeline A: Egocentric Visual Privacy (Layers 01 & 04)        │ 📡 Pipeline B: Encrypted Flow │
│                                                                  │    Meta-Activity Profiler     │
├──────────────────────────────────────────────────────────────────┼───────────────────────────────┤
│ • Real-time EgoBlur Gen1 JIT inference on edge (<22ms)           │ • Metadata-only packet stream │
│ • Solid, Gaussian, or pixelated face & plate redaction           │ • Direction, size, Δt bursts  │
│ • 46.7 FPS throughput on edge hardware                           │ • PySpark Louvain pruning     │
│ • Grounded Policy RAG (GDPR Art. 9, SITARA Tier 2)               │ • 2-Layer Relational GraphSAGE│
│ • Zero raw bystander biometrics transmitted                      │ • Isolation Forest exfiltration│
│ • Human-in-the-loop manual bounding box correction               │ • Open-Ear whisper & proof card│
└──────────────────────────────────────────────────────────────────┴───────────────────────────────┘
```

---

## ⚡ The Egocentric Privacy Crisis: The Tri-Fold Dilemma

Commercial smart glasses create three acute, conflicting operational dilemmas:

1. **The Wearer's Dilemma (Screenless Sensory Blindness)**:
   Smart glasses deliberately omit bulky visual screens to look like ordinary eyeglasses. A walking user cannot inspect JSON logs, read mobile alert dialogs, or tap screen buttons without severe collision hazards and cognitive overload. Notifications must be delivered through screenless, hands-free channels (such as bone-conduction audio).
2. **The Bystander's Dilemma (Involuntary Biometric Harvesting)**:
   Because the camera is mounted at eye level and records continuously, uninvolved pedestrians, vehicle drivers, and children have their facial geometry and license plates recorded without notice, consent, or opt-out options, violating GDPR Article 9, CCPA, and SITARA Consent Tiers.
3. **The Auditor's Dilemma (The Encrypted Audit Gap)**:
   In high-security environments (academic examination halls, semiconductor cleanrooms, medical facilities), smart-glasses traffic is encrypted under TLS 1.3. Payloads are opaque; traditional firewalls cannot differentiate between a legitimate 50 KB photo sync and an adversarial 4.2 Mbps video stream exfiltrating confidential intellectual property.

---

## 🛡️ 6-Layer Decoupled Defense Architecture

GlassShield organizes protection into 6 decoupled, testable layers communicating via the standardized `TelemetryTuple` contract:

| Layer | Component | Core Function | Implementation Details |
|---|---|---|---|
| **Layer 01** | On-Device Sensor & Privacy Engine | EgoBlur Gen1 TorchScript JIT face & license plate detection, OpenCV redaction, latency timing | [`layer_01_sensors_privacy/`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/layer_01_sensors_privacy/) — Sub-22ms edge latency (46.7 FPS) |
| **Layer 02** | Companion App & Transport Guard | Mutual TLS (mTLS) framing, schema verification, telemetry serialization | [`telemetry/`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/telemetry/) — Contract validation & logging |
| **Layer 03** | Network Anomaly Profiler | Encrypted packet token flow profiling (direction, size, delta_t), burst features, calibrated abstention | [`layer_03_network_anomalies/`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/layer_03_network_anomalies/) — Louvain & GraphSAGE |
| **Layer 04** | Cloud VLM Agent Security & Explainer | Defensible narrative synthesis, uncertainty calibration, section-grounded RAG | [`layer_04_vlm_agent/`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/layer_04_vlm_agent/) — Neo4j GraphRAG |
| **Layer 05** | Action Gate & Safety Boundary | Deterministic safety boundary enforcing ALLOW / BLOCK / CONFIRM | [`layer_04_vlm_agent/ai_explainer.py`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/layer_04_vlm_agent/ai_explainer.py) |
| **Layer 06** | Human Feedback & Active Learning | Human-in-the-loop audit review, manual box correction, empirical FPR tracking | [`app.py`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/app.py) & [`telemetry/telemetry_logger.py`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/telemetry/telemetry_logger.py) |

### System Architecture Flowchart
```
[ Smart Glasses Sensors ]
          │ (Raw Video Frame)
          ▼
┌──────────────────────────────────────────────┐
│ Layer 01: EgoBlur Gen1 JIT Vision Engine    │ ──> Redacts Faces & Plates (<22ms)
└──────────────────────────────────────────────┘
          │ (Redacted Frame + Metadata)
          ▼
┌──────────────────────────────────────────────┐
│ Layer 02: Transport Guard (mTLS Framing)    │ ──> Standardizes TelemetryTuple
└──────────────────────────────────────────────┘
          │ (Encrypted Packet Tokens)
          ▼
┌──────────────────────────────────────────────┐
│ Layer 03: PySpark & Relational GraphSAGE     │ ──> Louvain Pruning (Q=0.684)
│           Isolation Forest Profiler          │ ──> 100% Exfiltration Recall
└──────────────────────────────────────────────┘
          │ (Graph Embedding + Burst Vector)
          ▼
┌──────────────────────────────────────────────┐
│ Layer 04: Neo4j GraphRAG (37 Nodes, 56 Edges)│ ──> Grounded Regulatory Retrieval
└──────────────────────────────────────────────┘
          │ (Grounded Evidence + Uncertainty)
          ▼
┌──────────────────────────────────────────────┐
│ Layer 05: Action Gate (Safety Boundary)     │ ──> ALLOW / BLOCK / CONFIRM
└──────────────────────────────────────────────┘
          │
    ┌─────┴─────────────────────────────────────┐
    ▼                                           ▼
[ Wearer Audio Whisper ]          [ Auditor Visual Proof Card ]
(Open-Ear Bone Conduction <120ms) (HMAC-SHA256 Cryptographic Evidence)
    │                                           │
    └───────────────────┬───────────────────────┘
                        ▼
┌──────────────────────────────────────────────┐
│ Layer 06: Human-in-the-Loop Active Feedback │ ──> Slashing FPR by 87.3%
└──────────────────────────────────────────────┘
```

---

## 📊 Big Data Analytics, Graph Mining & Machine Learning

### 1. Big Data Sources & Characteristics
* **OVRseen Encrypted Metadata**: 1,200 real-world smart glasses network sessions capturing packet flow sizes, burst volumes, and inter-packet intervals ($\Delta t$).
* **EgoBlur Egocentric Vision Benchmark**: Multi-angle, variable-lighting egocentric video streams evaluated for real-time face and license plate redaction accuracy.
* **Codified Regulatory Knowledge Corpus**: 9 legal and institutional policy frameworks (SITARA Bystander Consent Tiers 1–3, GDPR Article 9 Biometrics, CCPA, IEEE 2089 Ethics, Cleanroom IP Confidentiality).

### 2. Unsupervised Louvain Community Discovery ($Q = 0.684$)
Using PySpark distributed processing across our 37-node Knowledge Graph paired with fleet flow records, Louvain community detection autonomously identifies four non-overlapping operational domains:
* **Community 1: Public Sidewalk & Bystander Obfuscation** (EgoBlur redaction, GDPR Art. 9, SITARA Tier 2).
* **Community 2: Academic Examination Integrity** (Proctor monitoring, exam codes, covert egress blocking).
* **Community 3: Semiconductor Cleanroom IP Protection** (Silicon schematics, camera disabling, mTLS enforcement).
* **Community 4: Testing Chamber Calibrated Abstention** (Safe open-set abstention when uncertainty $U \ge 0.40$).

### 3. 2-Layer Relational GraphSAGE ($AUC = 0.948$)
Wearable traffic is encrypted under TLS 1.3, making payload inspection impossible. A 2-layer GraphSAGE GNN propagates relational embeddings across intermediate graph nodes (`EncryptedPacketFlow` $	o$ `MetaActivity` $	o$ `RiskContext` $	o$ `MitigationAction`). This achieves a **0.948 Link Prediction AUC**, enabling the detection of stealth exfiltration disguised as benign cloud synchronization.

### 4. Zero-Day Covert Exfiltration Detection (Isolation Forest)
* **K-Means Flow Clustering ($Silhouette = 0.673$)**: Accurately groups encrypted flows into 5 operational archetypes (Idle, Photo Sync, Video Streaming, AI Interaction, Cloud Response).
* **Isolation Forest Anomaly Scoring**: Achieves **100% recall** on pulsed, periodic zero-day data leaks designed to bypass fixed firewall volume thresholds.
* **Calibrated Abstention Engine**: When flow features have high entropy ($U \ge 0.40$), the system strictly outputs a safe `UNKNOWN` verdict, preventing false accusations against users.

---

## 📈 Empirical Evaluation & Benchmark Results

We conducted a comprehensive 4-way ablation benchmark across 15 multi-hop complex egocentric queries:

| Retrieval Method | Recall@3 | Precision@3 | Grounding Accuracy | Query Latency | LLM Tokens | Edge Budget Status (<25ms) |
|---|---|---|---|---|---|---|
| **Baseline Vector RAG** | 33.3% | 60.0% | 0.0% (Hallucinates) | 28.4 ms | 1,840 | ❌ Exceeds Budget |
| **Naive Cypher Traversal** | 100.0% | 100.0% | 100.0% | 46.8 ms | 1,840 | ❌ Exceeds Budget |
| **Community GraphRAG** | 100.0% | 100.0% | 100.0% | **14.2 ms** | **420** (77.2% cut) | ✅ **Satisfies Budget** |
| **GNN-Enhanced GraphRAG** | **100.0%** | **100.0%** | **100.0%** | **16.5 ms** | **420** (77.2% cut) | ✅ **Satisfies Budget** |

### Key Benchmark Discoveries:
1. **Vector RAG Fails on Multi-Hop Regulatory Chains**: Standard vector embeddings retrieve isolated policy fragments without causal relationships, achieving only 33.3% recall.
2. **Community Pruning Slashes Latency by 69.7%**: Partitioning the graph with Louvain communities drops query execution from 46.8 ms to 14.2 ms.
3. **Sub-25ms Hardware Feasibility**: GNN-Enhanced GraphRAG executes in **16.5 ms**, well under the 25 ms wearable edge hardware deadline.
4. **Active Learning Reduces False Positives**: Proctor review overrides in Layer 06 dynamically retune edge weights, cutting the session False Positive Rate (FPR) by **87.3%**.

---

## 🎧 Dual-Audience Multimodal Generative AI Interfaces

Addressing the *Screenless Dilemma* and *Auditor Cognitive Overload*, GlassShield provides tailored multimodal presentations:

### 1. Wearer Interface: Real-Time Open-Ear Bone-Conduction Audio Whisper (<120ms)
* Delivered through open-ear bone conduction transducers built into smart-glasses temples.
* Uses neutral, non-accusatory phrasing strictly based on observable telemetry:
  > *"Notice: High-frequency egress stream detected in examination facility. Recording restricted under Academic Policy Section 4.2."*

### 2. Compliance Auditor Interface: One-Click Cryptographic Visual Proof Card
* Generated for security officers and proctors.
* Authenticated using **HMAC-SHA256**, bundling immutable packet timestamps, flow entropy, detection bounding boxes, and section-level legal citations.
* Includes one-click proctor review actions (**CONFIRM BLOCK**, **OVERRIDE / FALSE ALARM**).

---

## 🚀 Step-by-Step Execution & Reproducibility Guide

### Prerequisites
* Windows 10/11, macOS, or Ubuntu 20.04+
* Python 3.10 or 3.11
* Minimum 8 GB RAM

---

### Step 1: Clone the Repository & Setup Virtual Environment
```powershell
# Clone the repository
git clone https://github.com/VinceNguyen000/GlassShield.git
cd GlassShield

# Create virtual environment
python -m venv .venv

# Activate virtual environment:
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 2: Run the Automated Unit Test Suites
Verify system integrity by running our 13 automated unit tests:
```powershell
# Run Layer 01 & Human-AI workflow tests (8 tests)
.\.venv\Scripts\python -m unittest tests/test_human_ai_workflow.py

# Run Layer 03 Network Meta-Activity tests (5 tests)
.\.venv\Scripts\python -m unittest tests/test_network_meta_workflow.py
```
*Expected Result*: All 13 tests pass with 0 failures and 0 errors (`OK`).

---

### Step 3: Launch the Interactive Streamlit Application
```powershell
.\.venv\Scripts\streamlit run app.py --server.port 8501
```
Open your browser at `http://localhost:8501`:
* **Pipeline A**: Select *Egocentric Visual Privacy* to test live EgoBlur face/license plate redaction, grounded policy retrieval, and manual bounding box corrections.
* **Pipeline B**: Select *Encrypted Network Flow Profiler* to test encrypted flow burst detection, open-ear audio whisper synthesis, HMAC-SHA256 proof cards, and proctor review.

---

### Step 4: Run Big Data Analytics & Graph ML Pipeline
```powershell
.\.venv\Scripts\python layer_03_network_anomalies/challenge_4_analytics_pipeline.py
```
*Outputs*: Runs PySpark distributed preprocessing, computes Louvain Modularity ($Q=0.684$), trains 2-layer GraphSAGE GNN ($AUC=0.948$), and generates evaluation charts in `presentation/figures/`.

---

---

## 📁 Repository Directory Structure

```text
GlassShield/
├── app.py                              # Streamlit 11-component Human-AI Co-Design UI (Port 8501)
├── requirements.txt                    # Pinned Python package dependencies
├── README.md                           # Master GitHub documentation (this file)
├── AGENTS.md                           # Architecture and decision cheatsheet
├── glassshield_knowledge_graph.cypher  # Baseline 25-node / 27-edge Neo4j KG
├── glassshield_knowledge_graph_rag.cypher # Extended 37-node / 56-edge GraphRAG KG
│
├── layer_01_sensors_privacy/           # Layer 01: On-Device Vision Engine
│   ├── privacy_engine.py               # EgoBlur Gen1 JIT inference, NMS, OpenCV masking
│   ├── policy_rag.py                   # In-memory keyword & semantic legal policy retriever
│   ├── privacy_knowledge_base.json     # 9 regulatory policy frameworks
│   └── sample_data_loader.py           # 6 synthetic egocentric benchmark scenarios
│
├── layer_02_transport_guard/           # Layer 02: Transport Guard & mTLS Framing
│   ├── transport_guard.py              # Schema validation & TelemetryTuple serialization
│   └── __init__.py                     # Package exports
│
├── layer_03_network_anomalies/         # Layer 03: Big Data Analytics & Graph ML
│   ├── challenge_4_analytics_pipeline.py # PySpark, Louvain, K-Means & Isolation Forest
│   ├── gnn_enhanced_graphrag.py        # 2-layer GraphSAGE message passing & benchmark
│   └── meta_activity_engine.py         # Encrypted packet token flow profiling & bursts
│
├── layer_04_vlm_agent/                 # Layer 04: Cloud VLM & Grounded GraphRAG
│   ├── ai_explainer.py                 # Grounded narrative synthesis & uncertainty
│   └── graphrag_engine.py              # Neo4j GraphRAG query execution
│
├── layer_05_action_gate/               # Layer 05: Action Gate & Safety Boundary
│   ├── action_gate.py                  # ALLOW / BLOCK / CONFIRM & calibrated abstention
│   └── __init__.py                     # Package exports
│
├── layer_06_human_feedback/            # Layer 06: Human-in-the-Loop Feedback Store
│   ├── feedback_engine.py              # Proctor review, FPR calculation & active learning
│   └── __init__.py                     # Package exports
│
├── telemetry/                          # Standardized Cross-Layer Telemetry
│   └── telemetry_logger.py             # TelemetryTuple contract validator & JSONL logger
│
├── tests/                              # Automated Test Suite (13/13 Passing)
│   ├── test_human_ai_workflow.py       # 8 unit tests for visual privacy & human review
│   └── test_network_meta_workflow.py   # 5 unit tests for encrypted flow & defensible reasoning
│
└── presentation/figures/               # High-resolution benchmark figures & diagrams
    ├── ch4_pipeline_architecture.png
    ├── ch4_community_gnn_graphrag.png
    ├── ch4_clustering_anomaly_detection.png
    ├── ch4_evaluation_ablation_matrix.png
    ├── ch4_multimodal_proof_card.png
    ├── ch4_multimodal_genai_interface.png
    └── ch4_codesign_loop.png
```

---

## 🔒 Security, Privacy & Ethics Hygiene

* **No Payload Decryption**: GlassShield operates strictly on observable physical events, encrypted packet sizes, burst directions, and timing intervals ($\Delta t$). It never intercepts or decrypts TLS 1.3 payloads.
* **No Accusatory Accusations**: The system strictly separates observable telemetry from human intent. It never labels an individual as a "cheater" or "malicious actor"; it only flags anomalous network egress and cites applicable facility policies.
* **Safe Open-Set Abstention**: When packet entropy is high ($U \ge 0.40$), the system yields a safe `UNKNOWN` verdict rather than making a high-stakes false accusation.
* **Zero PII Exposure**: No personal identities, face embeddings, or private keys are stored or transmitted. All models run locally on the edge.

---

## 📜 License & Acknowledgments

This project is licensed under the **MIT License**.

### Course Recognition
Developed for **CS 5542 — Big Data Analytics & Applications** at the **University of Missouri-Kansas City (UMKC)**.  
We express our deepest gratitude to our course instructor, **Dr. Yugyung Lee**, and the teaching assistants for their guidance throughout the semester.
