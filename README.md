# GlassShield 🛡️🕶️
**Network-Aware Security and Privacy for AI Smart Glasses**  
*From Sensors and Companion Apps to Cloud Agents and Actions*

[![Status](https://img.shields.io/badge/Status-Active_Development-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-red.svg)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-TorchScript_JIT-orange.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-13%2F13_Passing-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

---

## 📖 What the Application Does

**GlassShield** is a Human–AI Co-Design platform and defense system addressing privacy, network anomalies, and policy enforcement for smart glasses (e.g., Meta Ray-Ban, Project Aria).

The application operates on a core scientific philosophy:  
> *"Tools calculate. RAG retrieves. LLMs interpret. Humans review and control."*

It provides two interactive primary workflow pipelines switchable directly via the Streamlit interface:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       GLASSSHIELD DUAL-PIPELINE                                         │
├──────────────────────────────────────────────────────────────────┬──────────────────────────────────────┤
│ 📸 Pipeline A: Egocentric Visual Privacy (Layer 01 & 04)         │ 📡 Pipeline B: Encrypted Network Flow│
│                                                                  │    Meta-Activity Profiler (Layer 03) │
├──────────────────────────────────────────────────────────────────┼──────────────────────────────────────┤
│ • Real-time EgoBlur Gen1 JIT inference on edge                   │ • Metadata-only packet token stream  │
│ • Gaussian, solid, or pixelated face & plate redaction          │ • Flow feature extraction & bursts   │
│ • Sub-33ms latency benchmark (< 30 FPS target)                  │ • Multi-modal optical presence sensor│
│ • 4 Interactive tabs: Visual Evidence, Grounded RAG,             │ • Calibrated abstention (UNKNOWN)    │
│   Telemetry Contract, and Human Review / Manual Boxes            │ • Defensible reasoning: no intent    │
│                                                                  │   accusations, section-level RAG     │
└──────────────────────────────────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 🏗️ 6-Layer Architecture

| Layer | Component | Core Function | Implementation Status |
|---|---|---|---|
| **Layer 01** | On-Device Sensor & Privacy Engine | EgoBlur Gen1 TorchScript JIT face & license plate detection, masking, latency benchmarking | ✅ **Implemented** (`layer_01_sensors_privacy/`) |
| **Layer 02** | Companion App & Transport Guard | Encrypted transport validation, mTLS framing, telemetry serialization | ✅ **Implemented** (`telemetry/`) |
| **Layer 03** | Network Anomaly Profiler | Encrypted packet token flow profiling (direction, size, delta_t), burst features, calibrated abstention | ✅ **Implemented** (`layer_03_network_anomalies/`) |
| **Layer 04** | Cloud VLM Agent Security & Explainer | Defensible narrative synthesis, uncertainty calibration, section-grounded RAG | ✅ **Implemented** (`layer_04_vlm_agent/`) |
| **Layer 05** | Action Gate & Safety Boundary | ALLOW / BLOCK / USER_CONFIRMATION_REQUIRED gate enforcement | ✅ **Implemented** (`layer_04_vlm_agent/ai_explainer.py`) |
| **Layer 06** | Human Review & Telemetry Store | Human-in-the-loop review, manual box correction, empirical FPR tracking, audit history | ✅ **Implemented** (`app.py`, `telemetry/`) |

---

## 🚀 How to Run

### ⚠️ Important: Read Before Running!
1. **Always use the virtual environment (`.venv`)**: Running `streamlit` directly in your base terminal may cause PyTorch binary mismatches.
2. **Port 8501 in use?**: Specify an alternate port (`--server.port 8502`) or free the port using the troubleshooting steps below.
3. **Offline-by-Default**: GlassShield runs 100% offline out-of-the-box using deterministic local RAG and TorchScript models. (Optional: add `GEMINI_API_KEY` to `.env` for cloud LLM explanations).

---

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/VinceNguyen000/GlassShield.git
cd GlassShield

# 2. Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Install EgoBlur (editable install from sibling repository)
git clone https://github.com/facebookresearch/EgoBlur.git ../EgoBlur
pip install -e ../EgoBlur

# 5. Place model weights
# Ensure EgoBlur Gen1 TorchScript models are in models/:
#   models/ego_blur_face_gen1.jit
#   models/ego_blur_lp_gen1.jit

# 6. (Optional) Configure .env file
echo GEMINI_API_KEY=your_key_here > .env
```

---

### 🖥️ Launching the Application

```powershell
# Run directly via the virtual environment:
.\.venv\Scripts\streamlit run app.py --server.port 8501
```

Open your browser to: **`http://localhost:8501`**

#### 🔧 Troubleshooting: Port 8501 is already in use
```powershell
# 1. Find the PID using port 8501
netstat -ano | findstr :8501

# 2. Terminate the process by PID
taskkill /PID <PID> /F

# 3. Relaunch
.\.venv\Scripts\streamlit run app.py --server.port 8501
```

---

### 🧪 Automated Test Suite (13/13 Tests Passing)

GlassShield includes two test suites covering visual privacy, encrypted network meta-activity inference, defensible policy reasoning, and schema compliance:

```bash
# Run all 13 unit tests across both suites:
.\.venv\Scripts\python -m unittest discover tests

# Or run individual test suites:
# Suite 1: Egocentric Visual Privacy & Human-AI Workflow (8 tests)
.\.venv\Scripts\python -m unittest tests/test_human_ai_workflow.py

# Suite 2: Encrypted Traffic Meta-Activity & Defensible Reasoning (5 tests)
.\.venv\Scripts\python -m unittest tests/test_network_meta_workflow.py
```

---

## 📂 Repository Structure

```text
GlassShield/
├── app.py                              # Streamlit 4-tab Human-AI Co-Design UI (Port 8501)
├── requirements.txt                    # Pinned Python package dependencies
├── README.md                           # Public onboarding, setup, and architecture documentation
├── AGENTS.md                           # Fast agent context & ADR cheatsheet
│
├── layer_01_sensors_privacy/           # Layer 01: On-Device Sensor & Privacy Engine
│   ├── privacy_engine.py               # EgoBlur Gen1 JIT inference, NMS, OpenCV masking, latency timing
│   ├── policy_rag.py                   # In-memory keyword & semantic overlap legal policy retriever
│   ├── privacy_knowledge_base.json     # 9 regulatory policies (SITARA, GDPR, CCPA, Exam, Cleanroom)
│   └── sample_data_loader.py           # 6 synthetic egocentric scenarios auto-generated on first run
│
├── layer_03_network_anomalies/         # Layer 03: Encrypted Traffic Meta-Activity Profiler
│   ├── __init__.py                     # Module exports
│   └── meta_activity_engine.py         # Packet token flow, window features, abstention & temporal fusion
│
├── layer_04_vlm_agent/                 # Layer 04 & 05: AI Explainer & Action Gate
│   ├── __init__.py                     # Module exports
│   └── ai_explainer.py                 # Grounded narrative synthesis, uncertainty metric, Action Gate verdict
│
├── telemetry/                          # Layer 02 & 06: Cross-Layer Telemetry Contract
│   ├── __init__.py                     # Module exports
│   └── telemetry_logger.py             # TelemetryTuple contract validator, JSONL logging, session metrics
│
├── tests/                              # Comprehensive Test Suite (13 Tests)
│   ├── test_human_ai_workflow.py       # 8 unit tests for visual privacy, RAG, and Human-AI loop (TC-01..08)
│   └── test_network_meta_workflow.py   # 5 unit tests for encrypted traffic, abstention, and defensibility (TC-N01..05)
│
├── models/                             # [GIT-IGNORED] EgoBlur Gen1 JIT model binaries (~400MB each)
│   ├── ego_blur_face_gen1.jit
│   └── ego_blur_lp_gen1.jit
│
└── presentation/                       # [GIT-IGNORED] Challenge 2 presentation deck & scripts
    └── Challenge_2_Slides.md           # 10-slide presentation script
```

---

## 📊 Privacy Knowledge Base (9 Policies)

The local RAG engine indexes 9 regulatory, legal, and operational policies from [`privacy_knowledge_base.json`](file:///c:/Users/VinceNguyen/.gemini/antigravity/GlassShield/layer_01_sensors_privacy/privacy_knowledge_base.json):

| Policy ID | Category | Jurisdiction / Standard | Recommended Action | Default Verdict |
|---|---|---|---|---|
| `POL-SITARA-001` | Bystander Consent | Smart Wearable Research (SYSNET-LUMS) | `MASK_PII` | `USER_CONFIRMATION_REQUIRED` |
| `POL-GDPR-ART9` | Regulatory Statute | European Union (EU/EEA) | `MASK_PII` | `USER_CONFIRMATION_REQUIRED` |
| `POL-CCPA-LP` | Regulatory Statute | California, USA | `MASK_PII` | `ALLOW` |
| `POL-ENT-CONF` | Enterprise Compliance | Enterprise Deployment | `BLOCK_IF_UNCERTAIN` | `USER_CONFIRMATION_REQUIRED` |
| `POL-CLEAN-ENV` | Standard Operations | Global / Default | `PRESERVE_CONTENT` | `ALLOW` |
| `POL-SITARA-UNCERTAIN` | Edge-Case Handling | Smart Wearable Research (SYSNET-LUMS) | `FLAG_UNCERTAINTY` | `USER_CONFIRMATION_REQUIRED` |
| `POL-EXAM-3.2` | Academic Integrity | Institutional Academic Council | `BLOCK_AND_FLAG_PROCTOR` | `BLOCK` |
| `POL-LAB-REC-01` | Corporate IP Protection | Advanced R&D Facility Security | `BLOCK_STREAM` | `BLOCK` |
| `POL-OPEN-SYNC-05` | Device Operations | Wearable Architecture Standard | `ALLOW_BACKGROUND_SYNC` | `ALLOW` |

---

## 🧠 Defensible AI Reasoning Contract

To ensure scientific rigor and avoid ethical pitfalls, GlassShield enforces a **Defensible Reasoning Contract** across Layer 03 and Layer 04:

1. **Observable Physical & Network Events Only**:  
   Classifications are restricted to factual operations: `IDLE`, `PHOTO`, `VIDEO/STREAM`, `AI_INTERACTION`, `RESPONSE`, `SYNC/UPLOAD`, or `UNKNOWN`.
2. **Strict Separation of Event vs. Intent**:  
   The system never infers subjective user intent or moral guilt (e.g., it never asserts *"the wearer is cheating"*). It objectively reports: *"Observable burst sequence matches optical capture followed by generative query during an evaluation interval per POL-EXAM-3.2."*
3. **Calibrated Open-Set Abstention (`UNKNOWN`)**:  
   If prediction confidence falls below the calibrated threshold (default: 65%) or inter-class margin is narrow, the model abstains to `UNKNOWN`, triggering `USER_CONFIRMATION_REQUIRED` rather than risking a false accusation.
4. **Multimodal Corroboration**:  
   Integrates non-content physical sensor corroboration (e.g., optical presence signature from AR waveguides) without intercepting or decrypting payload data.

---

## 🧪 Test Matrix Summary (13 Tests)

### Visual Privacy & Human-AI Workflow (`test_human_ai_workflow.py`)
- **TC-01 (Bystander Portrait)**: Single face detection, SITARA/GDPR retrieval, human approval.
- **TC-02 (Vehicle License Plate)**: License plate localized, CCPA policy matched.
- **TC-03 (Crowd Scene)**: Multi-entity table validation, bounding box coordinates sanity check.
- **TC-04 (Clean Room)**: True Negative verification, 0 PII entities, ALLOW verdict.
- **TC-05 (False Positive Audit)**: Human audit flags FP, FPR metric incremented, threshold adjustment clears FP.
- **TC-06 (Low-Light Edge Case)**: Low-confidence detection flags uncertainty, human draws manual box, forced blur applied.
- **TC-07 (Action Gate Override)**: Enterprise restricted zone policy blocks stream; human override verified.
- **TC-08 (TelemetryTuple Contract)**: Full schema validation against JSON serialization contract.

### Encrypted Traffic & Defensible Reasoning (`test_network_meta_workflow.py`)
- **TC-N01 (Exam Burst & LLM Query)**: `PHOTO -> AI_INTERACTION -> RESPONSE` sequence mapped to `POL-EXAM-3.2`; verifies non-accusatory language contract.
- **TC-N02 (Cleanroom High-Throughput Stream)**: Sustained video stream mapped to `POL-LAB-REC-01` -> `BLOCK`.
- **TC-N03 (Adversarial Jitter & Abstention)**: Ambiguous packet bursts trigger calibrated `UNKNOWN` abstention and `USER_CONFIRMATION_REQUIRED`.
- **TC-N04 (Optical Corroboration)**: Corroboration between optical presence indicator and network burst confirmed.
- **TC-N05 (Human Review Gate & Ledger)**: Human proctor overrides verdict; telemetry ledger audit trail verified.

---

## 🗺️ Roadmap & Milestones

| Milestone | Deliverable | Status |
|---|---|---|
| **Challenge 1** | Threat Landscape & Human Design Blueprint | ✅ **Complete** |
| **Challenge 2** | Egocentric Visual Privacy Vertical Slice (EgoBlur Gen1 + Policy RAG + UI) | ✅ **Complete** |
| **Challenge 3** | Encrypted Network Meta-Activity Profiler & Defensible Reasoning Engine | ✅ **Complete** |
| **Challenge 4** | Physical Prompt Injection Defense (Devil in the Lens / AgentDojo benchmark) | ⏳ *Next Up* |
| **Challenge 5** | End-to-End Multi-Layer System Integration Benchmark | ⏳ *Backlog* |

---

## 📚 Key References & Datasets

- **EgoBlur**: [facebookresearch/EgoBlur](https://github.com/facebookresearch/EgoBlur) (Meta Research, TorchScript Gen1)
- **SITARA**: [SYSNET-LUMS/SmartGlassesPrivacy](https://github.com/SYSNET-LUMS/SmartGlassesPrivacy) (Egocentric privacy evaluation)
- **OVRseen**: [UCI-Networking-Group/OVRseen](https://github.com/UCI-Networking-Group/OVRseen) (Encrypted VR/AR traffic flow profiling)
- **Devil in the Lens**: [arXiv:2607.10269](https://arxiv.org/abs/2607.10269) (Physical adversarial prompt injection)
- **AgentDojo**: [agency-enterprise/agent-dojo](https://github.com/agency-enterprise/agent-dojo) (Dynamic benchmark for agent safety)
