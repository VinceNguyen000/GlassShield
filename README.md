# GlassShield 🛡️🕶️
**Network-Aware Security and Privacy for AI Smart Glasses**  
*From Sensors and Companion Apps to Cloud Agents and Actions*

[![Status](https://img.shields.io/badge/Status-Active_Development-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-red.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

---

## 📖 What the Application Does

**GlassShield** is a Human–AI Co-Design application (CS 5542 Challenge 2) demonstrating the **First P1 Task**: on-device visual PII detection, privacy blurring, and a human verification gate for AI smart glasses.

The Streamlit app implements a complete vertical slice:

```
User Input → EgoBlur Detection → Policy RAG → Grounded AI Explanation → Evidence → Human Review & Correction
```

**Human and AI collaborate as follows:**

| Who | Does What |
|---|---|
| **Human** | Selects/uploads an egocentric frame, sets detection sensitivity, inspects visual evidence, accepts/overrides/corrects the AI verdict |
| **AI (Tools)** | EgoBlur Gen1 JIT models detect and localize bystander faces + vehicle license plates with confidence scores and latency timing |
| **AI (RAG)** | Policy retriever searches the Privacy Knowledge Base and returns top-3 matching regulatory citations (SITARA, GDPR Art. 9, CCPA, Enterprise) |
| **AI (Explainer)** | Synthesizes detections + citations into a grounded explanation with uncertainty score and recommended Action Gate verdict |

**All 11 required Streamlit components implemented:**  
Text/search input · File upload · Selection menus · Filters/sliders · Tables · Charts · Images · Retrieved evidence · AI explanation · Source/provenance · Human feedback

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- EgoBlur model weights (see **Data** section below)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/GlassShield.git
cd GlassShield

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install EgoBlur (editable install from separate repo)
git clone https://github.com/facebookresearch/EgoBlur.git ../EgoBlur
pip install -e ../EgoBlur

# 5. Download model weights (see Data section below)
# Place ego_blur_face_gen1.jit and ego_blur_lp_gen1.jit in models/

# 6. Launch the application
streamlit run app.py --server.port 8501
```

Open **http://localhost:8501** in your browser.

### Run Tests

```bash
python -m unittest tests/test_human_ai_workflow.py
# Expected: Ran 8 tests in ~90s ... OK
```

---

## 📂 Repository Structure

```text
GlassShield/
├── app.py                              # Main Streamlit application (Human-AI Co-Design UI)
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
│
├── layer_01_sensors_privacy/           # Layer 1: On-Device Sensor & Privacy Filter
│   ├── privacy_engine.py               # EgoBlur Gen1 JIT wrapper — detection, masking, latency
│   ├── policy_rag.py                   # Privacy Knowledge Base retriever (RAG)
│   ├── privacy_knowledge_base.json     # 6-policy regulatory corpus (SITARA, GDPR, CCPA...)
│   └── sample_data_loader.py           # Synthetic egocentric test scenario generator
│
├── layer_04_vlm_agent/                 # Layer 4: VLM Agent — AI Explanation & Gate
│   └── ai_explainer.py                 # Grounded explanation + Action Gate verdict synthesizer
│
├── telemetry/                          # Cross-Layer Telemetry Contract
│   └── telemetry_logger.py             # TelemetryTuple schema enforcement & JSONL logging
│
├── tests/                              # Automated Test Suite
│   └── test_human_ai_workflow.py       # 8 end-to-end test cases (TC-01 through TC-08)
│
├── models/                             # NOT committed — download separately (see below)
│   ├── ego_blur_face_gen1.jit          # EgoBlur Gen1 face detector
│   └── ego_blur_lp_gen1.jit            # EgoBlur Gen1 license plate detector
│
└── data/sitara_samples/                # NOT committed — auto-generated on first run
    ├── bystander_portrait.jpg          # Bystander face sample (uses test_output.jpg if present)
    ├── vehicle_plate.jpg               # Synthetic vehicle rear with license plate
    ├── crowded_street.jpg              # Multi-bystander public scene
    ├── clean_room.jpg                  # Indoor lounge — true negative (no PII)
    ├── low_light_edge.jpg              # Failure case — obscured low-light bystander
    └── textured_wall_art.jpg           # False positive audit — geometric wall art
```

---

## 📊 What Data It Uses

### Primary Model: EgoBlur (Meta Research)
- **Source**: [facebookresearch/EgoBlur](https://github.com/facebookresearch/EgoBlur)
- **Models**: `ego_blur_face_gen1.jit` (face), `ego_blur_lp_gen1.jit` (license plate)
- **Format**: TorchScript JIT — runs fully offline on CPU or GPU
- **Download**: From the EgoBlur GitHub releases or the Aria Research Kit
- **Note**: Model files are large (~400 MB each) and excluded from this repository via `.gitignore`

### Dataset Reference: SITARA (SYSNET-LUMS)
- **Source**: [SYSNET-LUMS/SmartGlassesPrivacy](https://github.com/SYSNET-LUMS/SmartGlassesPrivacy)
- **Description**: Authentic first-person egocentric recordings with manual face bounding box annotations for smart-glasses privacy compliance testing
- **Usage**: Sample bystander frame used as TC-01 benchmark input; full dataset for real FPR measurement (pending download)
- **Not committed**: Raw SITARA frames excluded per privacy guidelines

### Privacy Knowledge Base (RAG Corpus)
- **File**: `layer_01_sensors_privacy/privacy_knowledge_base.json` — **included in repo**
- **6 policies**:

| Policy ID | Coverage | Jurisdiction |
|---|---|---|
| `POL-SITARA-001` | Egocentric Bystander Consent Tier 2 | Smart Wearable Research |
| `POL-GDPR-ART9` | Biometric Data Processing Prohibition | EU/EEA |
| `POL-CCPA-LP` | Vehicle Identifier Privacy | California, USA |
| `POL-ENT-CONF` | Enterprise Restricted Zone Recording | Enterprise |
| `POL-CLEAN-ENV` | Standard Non-PII Stream Policy | Global Default |
| `POL-SITARA-UNCERTAIN` | Low-Confidence Edge-Case Safeguard | Smart Wearable Research |

### Synthetic Sample Data
Generated automatically on first run by `sample_data_loader.py` — no manual download required.

---

## 🧠 What AI Capability It Demonstrates

### 1. Vision Detection — EgoBlur (Tools Calculate)
- Runs on-device TorchScript JIT models with no cloud dependency
- Detects faces and license plates; applies configurable Gaussian blur, solid mask, or pixelation
- Measures per-frame **processing latency** against the 30 FPS target (< 33 ms)

### 2. Policy Retrieval — RAG (RAG Retrieves)
- Keyword + term-overlap retriever over the regulatory corpus
- Returns top-3 relevant policies based on detected entity type, search query, and confidence level
- Fully deterministic and auditable — no external embedding service needed

### 3. Grounded Explanation & Action Gate (LLM Interprets)
- Synthesizes detections + retrieved policies into a grounded compliance narrative
- Reports **uncertainty score** from confidence spread across detected entities
- Produces recommended verdict: `ALLOW` / `BLOCK` / `USER_CONFIRMATION_REQUIRED`
- Logs every event as a standardized `TelemetryTuple` (JSON) conforming to the cross-layer schema

### 4. Human–AI Feedback Loop
- Human accepts, overrides, or corrects the AI verdict
- Human adds manual bounding boxes for missed PII (False Negative correction)
- Session-wide **FPR** and **latency benchmark** tracked and visualized live
- All reviewed events exportable as `TelemetryTuple` JSON

---

## 🧪 Test Cases (8/8 Passing)

| TC | Scenario | Human–AI Check |
|---|---|---|
| TC-01 | Bystander Portrait | Face detected, GDPR/SITARA retrieved, human approves masking |
| TC-02 | Vehicle License Plate | CCPA policy top match, LP class verified |
| TC-03 | Crowd Scene | Multi-entity detection table, box integrity validated |
| TC-04 | Clean Room (True Negative) | Zero PII, Standard Policy retrieved, ALLOW verdict |
| TC-05 | **False Positive Audit** | Human flags FP, FPR counter increments, threshold refinement clears it |
| TC-06 | **Low-Light Failure Case** | High uncertainty flagged, human adds manual box, forced blur applied |
| TC-07 | **Action Gate Override** | Enterprise policy blocks stream, human overrides to BLOCK |
| TC-08 | TelemetryTuple Schema | All required JSON fields validated against `memory.md` contract |

---

## 🔲 What Remains to Be Developed

| Item | Priority | Notes |
|---|---|---|
| Real SITARA FPR benchmark | **P1** | Download full SITARA dataset; compute FPR against ground truth labels |
| Gemini API multimodal explanation | **P2** | `ai_explainer.py` has API key hook ready; add `google-genai` SDK integration |
| Layer 03 Network Anomaly Profiler | **P2** | OVRseen encrypted traffic classifier (Challenge 3 milestone) |
| Layer 04 Prompt Injection Defense | **P3** | Devil in the Lens + AgentDojo harness (Challenge 4 milestone) |
| Layer 05 Action Gate Policy Engine | **P3** | Formal policy enforcement across all layers (Challenge 5 integration) |
| Video stream inference | **P4** | Extend `privacy_engine.py` to process frame-by-frame from `.mp4` |

---

## 📚 Key References & Datasets

- **SITARA**: [SYSNET-LUMS/SmartGlassesPrivacy](https://github.com/SYSNET-LUMS/SmartGlassesPrivacy)
- **EgoBlur**: [facebookresearch/EgoBlur](https://github.com/facebookresearch/EgoBlur)
- **OVRseen**: [UCI-Networking-Group/OVRseen](https://github.com/UCI-Networking-Group/OVRseen)
- **Devil in the Lens**: [arXiv:2607.10269](https://arxiv.org/abs/2607.10269)
- **AgentDojo**: [agency-enterprise/agent-dojo](https://github.com/agency-enterprise/agent-dojo)
