// ==============================================================================
// GlassShield 🛡️🕶️ Knowledge Graph (GraphRAG Extended Edition)
// Course: CS 5542 - Challenge 3: Human–AI Co-Design — GraphRAG with Neo4j (Part 1)
// Author: Vien (Vince) Nguyen
//
// SUMMARY OF EXTENSIONS FOR GRAPHRAG:
// 1. Refined Entities:
//    - Added `MitigationAction` nodes representing on-device & network mitigations.
//    - Enriched all nodes with `rag_summary` and `text_description` for hybrid retrieval.
// 2. Refined Relationships:
//    - Added bidirectional evidence edges: `[:GROUNDED_IN]`, `[:CORROBORATED_BY]`.
//    - Added defense edges: `[:MITIGATED_BY]`, `[:TRIGGERS_ACTION]`, `[:PROTECTS_AGAINST]`.
// 3. Schema Indexes:
//    - Added Neo4j Full-Text Indexes on policies, activities, verdicts, and entities.
// 4. Research Grounding:
//    - OVRseen (PETS 2022): Transport layer metadata (destination_host, protocol).
//    - SITARA / EgoBlur: Consent tiers and on-device latency budget properties.
// ==============================================================================

// ------------------------------------------------------------------------------
// STEP 1: SCHEMA CONSTRAINTS & INDEXES
// ------------------------------------------------------------------------------
CREATE CONSTRAINT c_obs_id IF NOT EXISTS FOR (o:SensorObservation) REQUIRE o.obs_id IS UNIQUE;
CREATE CONSTRAINT c_entity_id IF NOT EXISTS FOR (e:DetectedEntity) REQUIRE e.entity_id IS UNIQUE;
CREATE CONSTRAINT c_burst_id IF NOT EXISTS FOR (b:NetworkBurst) REQUIRE b.burst_id IS UNIQUE;
CREATE CONSTRAINT c_activity_id IF NOT EXISTS FOR (a:MetaActivity) REQUIRE a.activity_id IS UNIQUE;
CREATE CONSTRAINT c_policy_id IF NOT EXISTS FOR (p:CompliancePolicy) REQUIRE p.policy_id IS UNIQUE;
CREATE CONSTRAINT c_verdict_id IF NOT EXISTS FOR (v:ActionGateVerdict) REQUIRE v.verdict_id IS UNIQUE;
CREATE CONSTRAINT c_action_id IF NOT EXISTS FOR (m:MitigationAction) REQUIRE m.action_id IS UNIQUE;

CREATE INDEX idx_obs_timestamp IF NOT EXISTS FOR (o:SensorObservation) ON (o.timestamp_iso);
CREATE INDEX idx_activity_type IF NOT EXISTS FOR (a:MetaActivity) ON (a.activity_type);
CREATE INDEX idx_verdict_status IF NOT EXISTS FOR (v:ActionGateVerdict) ON (v.status);
CREATE INDEX idx_burst_host IF NOT EXISTS FOR (b:NetworkBurst) ON (b.destination_host);

// Neo4j Full-Text Search Indexes for GraphRAG Hybrid Retrieval
CREATE FULLTEXT INDEX rag_policy_fulltext IF NOT EXISTS 
FOR (p:CompliancePolicy) ON EACH [p.title, p.citation, p.rag_summary, p.mandated_action];

CREATE FULLTEXT INDEX rag_verdict_fulltext IF NOT EXISTS 
FOR (v:ActionGateVerdict) ON EACH [v.status, v.narrative_reasoning, v.rag_summary];

CREATE FULLTEXT INDEX rag_activity_fulltext IF NOT EXISTS 
FOR (a:MetaActivity) ON EACH [a.activity_type, a.rag_summary, a.risk_category];

CREATE FULLTEXT INDEX rag_entity_fulltext IF NOT EXISTS 
FOR (e:DetectedEntity) ON EACH [e.category, e.rag_summary, e.sensitivity_level];

CREATE FULLTEXT INDEX rag_burst_fulltext IF NOT EXISTS 
FOR (b:NetworkBurst) ON EACH [b.burst_id, b.destination_host, b.rag_summary];

// ------------------------------------------------------------------------------
// STEP 2: KNOWLEDGE GRAPH DATA INGESTION (EXTENDED WITH GRAPHRAG PROPERTIES)
// ------------------------------------------------------------------------------

// --- 1. SENSOR OBSERVATIONS (W3C SOSA/SSN Grounding) ---
CREATE (obs1:SensorObservation {
    obs_id: "OBS-2026-EXAM-01",
    timestamp_iso: "2026-10-09T14:32:01.120Z",
    source_sensor: "RGB_CAMERA_1264x1264",
    frame_index: 104,
    device_model: "Ray-Ban Meta Gen2",
    environment: "University Examination Hall",
    optical_presence_verified: true,
    rag_summary: "Sensor capture OBS-2026-EXAM-01 recorded by Ray-Ban Meta Gen2 RGB camera at 14:32:01 UTC in University Examination Hall. Frame contains high-contrast academic evaluation text on an exam booklet with verified optical presence."
})
CREATE (obs2:SensorObservation {
    obs_id: "OBS-2026-STREET-02",
    timestamp_iso: "2026-10-09T15:10:22.450Z",
    source_sensor: "RGB_CAMERA_1264x1264",
    frame_index: 665,
    device_model: "Ray-Ban Meta Gen2",
    environment: "Downtown Public Sidewalk",
    optical_presence_verified: true,
    rag_summary: "Sensor capture OBS-2026-STREET-02 recorded in public outdoor space on a commercial sidewalk. Frame captures pedestrians and parked vehicles in the field of view requiring bystander privacy protection."
})
CREATE (obs3:SensorObservation {
    obs_id: "OBS-2026-LAB-03",
    timestamp_iso: "2026-10-09T16:04:15.800Z",
    source_sensor: "RGB_CAMERA_1264x1264",
    frame_index: 1200,
    device_model: "Project Aria",
    environment: "Semiconductor Cleanroom Facility",
    optical_presence_verified: true,
    rag_summary: "Sensor capture OBS-2026-LAB-03 recorded by Project Aria inside a secured cleanroom perimeter. Optical sensor detected high-resolution active monitor displaying proprietary wafer schematic designs."
})
CREATE (obs4:SensorObservation {
    obs_id: "OBS-2026-AUDIT-04",
    timestamp_iso: "2026-10-09T16:45:00.210Z",
    source_sensor: "OPTICAL_WAVEGUIDE",
    frame_index: 2301,
    device_model: "Ray-Ban Meta Gen2",
    environment: "Audited Testing Chamber",
    optical_presence_verified: true,
    rag_summary: "Sensor capture OBS-2026-AUDIT-04 recorded optical waveguide trigger under synthetic adversarial jitter. Sensor telemetry exhibits ambiguous packet timing characteristics requiring calibrated open-set abstention."
})
CREATE (obs5:SensorObservation {
    obs_id: "OBS-2026-SYNC-05",
    timestamp_iso: "2026-10-09T17:00:00.000Z",
    source_sensor: "COMPANION_BLE_DAEMON",
    frame_index: 0,
    device_model: "Ray-Ban Meta Gen2",
    environment: "User Home Office",
    optical_presence_verified: false,
    rag_summary: "Sensor capture OBS-2026-SYNC-05 represents an idle state with zero optical sensor activity. The companion BLE daemon initiated periodic background telemetry synchronization."
})

// --- 2. DETECTED ENTITIES (W3C DPV / EgoBlur Detections) ---
CREATE (ent1:DetectedEntity {
    entity_id: "ENT-EXAM-DOC-01",
    category: "DOCUMENT_EXAM_TEXT",
    sensitivity_level: "CRITICAL_ASSESSMENT",
    confidence: 0.942,
    bbox: [120, 310, 540, 890],
    area_percentage: 24.5,
    redaction_applied: false,
    redaction_type: "NONE",
    rag_summary: "Entity ENT-EXAM-DOC-01 is a detected printed exam document occupying 24.5% of the frame with 94.2% confidence. Zero redaction was applied at the visual layer, posing an academic integrity risk if uploaded."
})
CREATE (ent2:DetectedEntity {
    entity_id: "ENT-STREET-FACE-01",
    category: "FACE",
    sensitivity_level: "REGULATED_BIOMETRIC",
    confidence: 0.965,
    bbox: [154, 443, 562, 673],
    area_percentage: 8.7,
    redaction_applied: true,
    redaction_type: "GAUSSIAN_BLUR",
    rag_summary: "Entity ENT-STREET-FACE-01 is a bystander facial biometric detected with 96.5% confidence. EgoBlur Gen1 JIT applied on-device Gaussian blur filter prior to local storage, ensuring GDPR Art. 9 compliance."
})
CREATE (ent3:DetectedEntity {
    entity_id: "ENT-STREET-LP-02",
    category: "LICENSE_PLATE",
    sensitivity_level: "VEHICLE_IDENTIFIER",
    confidence: 0.912,
    bbox: [620, 810, 680, 950],
    area_percentage: 2.1,
    redaction_applied: true,
    redaction_type: "SOLID_MASK",
    rag_summary: "Entity ENT-STREET-LP-02 is a vehicle license plate detected with 91.2% confidence in the street scene. Protected with an on-device solid black privacy mask per SITARA Tier 2 guidelines."
})
CREATE (ent4:DetectedEntity {
    entity_id: "ENT-LAB-SCREEN-01",
    category: "PROPRIETARY_DISPLAY",
    sensitivity_level: "HIGH_TRADE_SECRET",
    confidence: 0.887,
    bbox: [50, 100, 700, 1100],
    area_percentage: 42.0,
    redaction_applied: false,
    redaction_type: "NONE",
    rag_summary: "Entity ENT-LAB-SCREEN-01 is a proprietary cleanroom display terminal occupying 42.0% of the visual field. Contains unredacted trade secret schematics governed by strict cleanroom non-transmission mandates."
})

// --- 3. NETWORK BURSTS (OASIS STIX / OVRseen Flow Profiling) ---
CREATE (burst1:NetworkBurst {
    burst_id: "BURST-EXAM-PHOTO-01",
    timestamp_iso: "2026-10-09T14:32:01.240Z",
    direction: "UPLINK",
    total_bytes: 49152,
    packet_count: 38,
    duration_ms: 185.0,
    mean_inter_arrival_ms: 4.8,
    destination_host: "api.meta-companion.internal:443",
    transport_protocol: "TLS1.3/TCP",
    rag_summary: "Network burst BURST-EXAM-PHOTO-01 is an uplink transmission of 48 KB across 38 packets over TLS 1.3 occurring 120ms after exam document capture, matching the exact encrypted signature of a high-resolution photo upload."
})
CREATE (burst2:NetworkBurst {
    burst_id: "BURST-EXAM-LLM-02",
    timestamp_iso: "2026-10-09T14:32:01.890Z",
    direction: "UPLINK",
    total_bytes: 12288,
    packet_count: 14,
    duration_ms: 92.0,
    mean_inter_arrival_ms: 6.5,
    destination_host: "api.openai.com:443",
    transport_protocol: "TLS1.3/TCP",
    rag_summary: "Network burst BURST-EXAM-LLM-02 transmits 12 KB to cloud AI endpoint api.openai.com 650ms after the photo upload, indicating an interactive vision-language query containing exam questions."
})
CREATE (burst3:NetworkBurst {
    burst_id: "BURST-STREET-SYNC-01",
    timestamp_iso: "2026-10-09T15:10:22.580Z",
    direction: "UPLINK",
    total_bytes: 4096,
    packet_count: 5,
    duration_ms: 45.0,
    mean_inter_arrival_ms: 9.0,
    destination_host: "telemetry.smartglasses.net:443",
    transport_protocol: "TLS1.3/TCP",
    rag_summary: "Network burst BURST-STREET-SYNC-01 is a small 4 KB uplink burst consisting of 5 packets sent to the telemetry aggregation server, representing redacted metadata synchronization."
})
CREATE (burst4:NetworkBurst {
    burst_id: "BURST-LAB-STREAM-01",
    timestamp_iso: "2026-10-09T16:04:15.910Z",
    direction: "UPLINK",
    total_bytes: 524288,
    packet_count: 412,
    duration_ms: 1020.0,
    mean_inter_arrival_ms: 2.4,
    destination_host: "live-rtsp.external-cdn.io:8554",
    transport_protocol: "QUIC/UDP",
    rag_summary: "Network burst BURST-LAB-STREAM-01 is a continuous high-volume uplink transmission of 512 KB across 412 packets over QUIC/UDP, characteristic of active unencrypted real-time video streaming."
})
CREATE (burst5:NetworkBurst {
    burst_id: "BURST-JITTER-AMBIG-01",
    timestamp_iso: "2026-10-09T16:45:00.320Z",
    direction: "BIDIRECTIONAL",
    total_bytes: 18432,
    packet_count: 22,
    duration_ms: 310.0,
    mean_inter_arrival_ms: 14.1,
    destination_host: "ingress-relay.unknown-proxy.org:443",
    transport_protocol: "TLS1.3/TCP",
    rag_summary: "Network burst BURST-JITTER-AMBIG-01 is an ambiguous bidirectional flow of 18 KB with erratic inter-arrival timing (14.1ms) routed through a relay proxy, causing classification model ambiguity."
})
CREATE (burst6:NetworkBurst {
    burst_id: "BURST-SYS-HEARTBEAT-01",
    timestamp_iso: "2026-10-09T17:00:00.080Z",
    direction: "BIDIRECTIONAL",
    total_bytes: 1024,
    packet_count: 2,
    duration_ms: 12.0,
    mean_inter_arrival_ms: 6.0,
    destination_host: "device-health.smartglasses.internal:8443",
    transport_protocol: "mTLS/TCP",
    rag_summary: "Network burst BURST-SYS-HEARTBEAT-01 is a minimal 1 KB bidirectional device health heartbeat transmitted over mutual TLS during device standby."
})

// --- 4. META ACTIVITIES (Behavioral Operational States) ---
CREATE (act1:MetaActivity {
    activity_id: "ACT-PHOTO-CAPTURE",
    activity_type: "PHOTO",
    risk_category: "POTENTIAL_EXFILTRATION",
    confidence: 0.94,
    is_open_set_abstention: false,
    protocol_inferred: "HTTPS/TLS1.3",
    rag_summary: "MetaActivity ACT-PHOTO-CAPTURE inferred from burst profile (48 KB, 185ms) with 94.0% confidence. Indicates a discrete still image capture transmitted across the network."
})
CREATE (act2:MetaActivity {
    activity_id: "ACT-AI-QUERY",
    activity_type: "AI_INTERACTION",
    risk_category: "ACADEMIC_INTEGRITY_VIOLATION",
    confidence: 0.91,
    is_open_set_abstention: false,
    protocol_inferred: "HTTPS/TLS1.3",
    rag_summary: "MetaActivity ACT-AI-QUERY represents cloud generative AI inference inferred from secondary 12 KB uplink burst with 91.0% confidence, indicating real-time automated assistance."
})
CREATE (act3:MetaActivity {
    activity_id: "ACT-VIDEO-STREAM",
    activity_type: "VIDEO_STREAM",
    risk_category: "TRADE_SECRET_EXFILTRATION",
    confidence: 0.98,
    is_open_set_abstention: false,
    protocol_inferred: "QUIC/UDP",
    rag_summary: "MetaActivity ACT-VIDEO-STREAM represents continuous high-bandwidth video exfiltration (>500 KB/s) inferred with 98.0% confidence over UDP."
})
CREATE (act4:MetaActivity {
    activity_id: "ACT-ABSTAIN-UNKNOWN",
    activity_type: "UNKNOWN",
    risk_category: "CALIBRATED_ABSTENTION",
    confidence: 0.42,
    is_open_set_abstention: true,
    protocol_inferred: "BLE_L2CAP",
    rag_summary: "MetaActivity ACT-ABSTAIN-UNKNOWN triggered when burst classification confidence fell below the 70% threshold to 42.0%. Enforces open-set abstention rather than subjective guessing."
})
CREATE (act5:MetaActivity {
    activity_id: "ACT-DEVICE-SYNC",
    activity_type: "SYNC_UPLOAD",
    risk_category: "BENIGN_MAINTENANCE",
    confidence: 0.95,
    is_open_set_abstention: false,
    protocol_inferred: "HTTPS/TLS1.3",
    rag_summary: "MetaActivity ACT-DEVICE-SYNC verified as routine background telemetry upload with 95.0% confidence, posing zero privacy threat."
})

// --- 5. COMPLIANCE POLICIES (Regulatory & Institutional Rules) ---
CREATE (pol1:CompliancePolicy {
    policy_id: "POL-EXAM-3.2",
    title: "Prohibition of Electronic Assistance and Capture During Evaluation",
    jurisdiction: "Institutional Academic Council",
    mandated_action: "BLOCK_AND_FLAG_PROCTOR",
    citation: "Sec 3.2.1 Unauthorized AI Inference",
    legal_article: "Academic Code Section 3.2.1",
    enforcement_severity: "STRICT_BLOCK",
    rag_summary: "Policy POL-EXAM-3.2 strictly prohibits any capture or transmission of evaluation material and forbids cloud AI query generation during examinations. Mandates immediate network flow termination and proctor alerting."
})
CREATE (pol2:CompliancePolicy {
    policy_id: "POL-GDPR-ART9",
    title: "Processing of Special Categories of Personal Data (Biometric Facial Data)",
    jurisdiction: "European Union GDPR",
    mandated_action: "MANDATORY_ON_DEVICE_REDACTION",
    citation: "Article 9(1) Biometric Identification",
    legal_article: "GDPR Article 9(1)",
    enforcement_severity: "MANDATORY_REDACT",
    rag_summary: "Policy POL-GDPR-ART9 mandates that biometric data (facial images) captured by wearable sensors in public spaces must be permanently redacted at the edge before persistent storage or network transmission."
})
CREATE (pol3:CompliancePolicy {
    policy_id: "POL-SITARA-001",
    title: "SITARA Bystander Consent Taxonomy Tier 2",
    jurisdiction: "Smart Wearable Research (SYSNET-LUMS)",
    mandated_action: "MASK_NON_CONSENTING_BYSTANDERS",
    citation: "Sec 4.1 Incidental Capture",
    legal_article: "SITARA Tier 2 Framework",
    enforcement_severity: "MANDATORY_REDACT",
    rag_summary: "Policy POL-SITARA-001 governs incidental bystander capture in wearable computing. Mandates obfuscation of non-consenting individuals and vehicle registration identifiers using localized bounding box masks."
})
CREATE (pol4:CompliancePolicy {
    policy_id: "POL-LAB-REC-01",
    title: "Corporate IP & Cleanroom Zero-Transmission Mandate",
    jurisdiction: "Advanced R&D Facility Security",
    mandated_action: "BLOCK_STREAM",
    citation: "Rule 12 Confidential IP",
    legal_article: "Cleanroom Security Directive Rule 12",
    enforcement_severity: "STRICT_BLOCK",
    rag_summary: "Policy POL-LAB-REC-01 designates secure cleanrooms as zero-transmission zones. Any high-bandwidth continuous video stream detected within the cleanroom perimeter must be terminated at the Action Gate."
})
CREATE (pol5:CompliancePolicy {
    policy_id: "POL-SITARA-UNCERTAIN",
    title: "Edge-Case Handling & Calibrated Abstention Standard",
    jurisdiction: "Smart Wearable Research (SYSNET-LUMS)",
    mandated_action: "FLAG_UNCERTAINTY",
    citation: "Sec 5.3 Ambiguous Flow Protocol",
    legal_article: "Defensible Reasoning Contract Sec 5.3",
    enforcement_severity: "AUDIT_REVIEW",
    rag_summary: "Policy POL-SITARA-UNCERTAIN governs ambiguous network or sensor signals. When confidence drops below threshold, automated systems must abstain to UNKNOWN and request human supervisor confirmation."
})
CREATE (pol6:CompliancePolicy {
    policy_id: "POL-OPEN-SYNC-05",
    title: "Wearable Architecture Standard Device Telemetry Allowance",
    jurisdiction: "Global Default Standard",
    mandated_action: "ALLOW_BACKGROUND_SYNC",
    citation: "Sec 1.4 Heartbeat Protocol",
    legal_article: "Wearable Device Specification Sec 1.4",
    enforcement_severity: "UNRESTRICTED",
    rag_summary: "Policy POL-OPEN-SYNC-05 permits periodic low-bandwidth device telemetry and cryptographic heartbeat verification during idle wearable device states."
})

// --- 6. MITIGATION ACTIONS (Technical Defenses & Enforcements) ---
CREATE (mit1:MitigationAction {
    action_id: "MIT-SOCKET-RST-01",
    name: "TCP Reset & Cloud Endpoint Termination",
    action_type: "NETWORK_GATE_INTERCEPT",
    target_layer: "Layer 05 Action Gate",
    latency_ms: 12.5,
    enforcement_mechanism: "Kernel iptables / eBPF TCP RST injection",
    rag_summary: "Mitigation MIT-SOCKET-RST-01 actively terminates unauthorized uplink sockets to cloud AI services within 12.5ms, preventing prompt and image exfiltration."
})
CREATE (mit2:MitigationAction {
    action_id: "MIT-EGOBLUR-FACE-02",
    name: "EgoBlur Gen1 JIT Gaussian Blur",
    action_type: "ON_DEVICE_PII_REDACTION",
    target_layer: "Layer 01 Sensor Privacy",
    latency_ms: 21.4,
    enforcement_mechanism: "PyTorch TorchScript Gen1 NMS + OpenCV 51x51 Gaussian Kernel",
    rag_summary: "Mitigation MIT-EGOBLUR-FACE-02 executes on companion hardware in 21.4ms to obfuscate bystander facial biometrics before network serialization."
})
CREATE (mit3:MitigationAction {
    action_id: "MIT-EGOBLUR-LP-03",
    name: "EgoBlur Gen1 JIT Solid Masking",
    action_type: "ON_DEVICE_PII_REDACTION",
    target_layer: "Layer 01 Sensor Privacy",
    latency_ms: 18.2,
    enforcement_mechanism: "Bounding box solid zero-pixel filling",
    rag_summary: "Mitigation MIT-EGOBLUR-LP-03 applies solid black pixel masking over vehicle license plates in 18.2ms, eliminating vehicle identification risks."
})
CREATE (mit4:MitigationAction {
    action_id: "MIT-FIREWALL-BLOCK-04",
    name: "Cleanroom Perimeter Stream Blackhole",
    action_type: "NETWORK_GATE_INTERCEPT",
    target_layer: "Layer 05 Action Gate",
    latency_ms: 8.4,
    enforcement_mechanism: "QUIC/UDP egress packet drop",
    rag_summary: "Mitigation MIT-FIREWALL-BLOCK-04 severs external video streaming connections from cleanrooms within 8.4ms, protecting intellectual property."
})
CREATE (mit5:MitigationAction {
    action_id: "MIT-PROCTOR-ESCALATE-05",
    name: "Human-in-the-Loop Proctor Dispatch",
    action_type: "AUDIT_ESCALATION",
    target_layer: "Layer 06 Human Feedback",
    latency_ms: 45.0,
    enforcement_mechanism: "WebSocket push alert with uncertainty telemetry",
    rag_summary: "Mitigation MIT-PROCTOR-ESCALATE-05 dispatches an alert to the human proctor dashboard when automated models abstain due to adversarial jitter."
})
CREATE (mit6:MitigationAction {
    action_id: "MIT-PASSTHROUGH-ALLOW-06",
    name: "Verified Benign Passthrough",
    action_type: "PERMITTED_TRANSIT",
    target_layer: "Layer 05 Action Gate",
    latency_ms: 1.1,
    enforcement_mechanism: "Bypass filter for validated mTLS telemetry",
    rag_summary: "Mitigation MIT-PASSTHROUGH-ALLOW-06 validates cryptographic headers and allows non-sensitive device telemetry without degradation."
})

// --- 7. ACTION GATE VERDICTS (Enforceable Decision & Reason) ---
CREATE (vrd1:ActionGateVerdict {
    verdict_id: "VRD-EXAM-BLOCK-01",
    status: "BLOCK",
    uncertainty_score: 0.05,
    human_override: false,
    narrative_reasoning: "Observable burst sequence matches camera capture followed by cloud generative AI query during examination interval per POL-EXAM-3.2.",
    rag_summary: "Verdict VRD-EXAM-BLOCK-01 issued a hard BLOCK on exam room transmission. Unredacted exam text capture was corroborated by a 48 KB photo uplink followed by a 12 KB query to api.openai.com, triggering socket termination MIT-SOCKET-RST-01."
})
CREATE (vrd2:ActionGateVerdict {
    verdict_id: "VRD-STREET-ALLOW-02",
    status: "ALLOW",
    uncertainty_score: 0.04,
    human_override: false,
    narrative_reasoning: "Bystander facial biometrics localized and redacted on-device prior to storage. Complies with GDPR Art. 9 and SITARA Tier 2.",
    rag_summary: "Verdict VRD-STREET-ALLOW-02 permitted transmission (ALLOW) because all detected bystander faces and license plates were verified as redacted on-device via EgoBlur Gen1 JIT prior to sync."
})
CREATE (vrd3:ActionGateVerdict {
    verdict_id: "VRD-LAB-BLOCK-03",
    status: "BLOCK",
    uncertainty_score: 0.02,
    human_override: false,
    narrative_reasoning: "Continuous high-throughput uplink video stream detected inside restricted cleanroom perimeter per POL-LAB-REC-01.",
    rag_summary: "Verdict VRD-LAB-BLOCK-03 enforced a BLOCK on cleanroom video stream. Unredacted monitor schematics coupled with 512 KB continuous QUIC stream violated Rule 12 zero-transmission policy."
})
CREATE (vrd4:ActionGateVerdict {
    verdict_id: "VRD-JITTER-CONFIRM-04",
    status: "USER_CONFIRMATION_REQUIRED",
    uncertainty_score: 0.58,
    human_override: false,
    narrative_reasoning: "Burst profile confidence below calibrated threshold (42%). Model abstains to UNKNOWN; proctor confirmation required per POL-SITARA-UNCERTAIN.",
    rag_summary: "Verdict VRD-JITTER-CONFIRM-04 abstained from automated judgment (USER_CONFIRMATION_REQUIRED). High uncertainty (0.58) and adversarial burst timing triggered human proctor escalation."
})
CREATE (vrd5:ActionGateVerdict {
    verdict_id: "VRD-SYNC-ALLOW-05",
    status: "ALLOW",
    uncertainty_score: 0.01,
    human_override: false,
    narrative_reasoning: "Periodic background telemetry heartbeat verified with standard wearable profile per POL-OPEN-SYNC-05.",
    rag_summary: "Verdict VRD-SYNC-ALLOW-05 permitted routine background sync (ALLOW) with near-zero uncertainty (0.01), confirming benign mTLS heartbeat traffic."
})

// ------------------------------------------------------------------------------
// STEP 3: CONNECTING RELATIONSHIPS (FORWARD, CAUSAL, AND BIDIRECTIONAL EVIDENCE)
// ------------------------------------------------------------------------------

// 1. [:DETECTED] (Observation -> DetectedEntity)
CREATE (obs1)-[:DETECTED {detector: "egoblur_gen1_jit", confidence: 0.942}]->(ent1)
CREATE (obs2)-[:DETECTED {detector: "egoblur_gen1_jit", confidence: 0.965}]->(ent2)
CREATE (obs2)-[:DETECTED {detector: "egoblur_gen1_jit", confidence: 0.912}]->(ent3)
CREATE (obs3)-[:DETECTED {detector: "egoblur_gen1_jit", confidence: 0.887}]->(ent4)

// 2. [:TEMPORALLY_CORRELATED_WITH] (Observation -> NetworkBurst with delta_t_ms)
CREATE (obs1)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 120.0, corroborated: true}]->(burst1)
CREATE (obs2)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 130.0, corroborated: true}]->(burst3)
CREATE (obs3)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 110.0, corroborated: true}]->(burst4)
CREATE (obs4)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 110.0, corroborated: false}]->(burst5)
CREATE (obs5)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 80.0, corroborated: true}]->(burst6)

// 3. [:PRECEDES] (Temporal sequence chaining between bursts)
CREATE (burst1)-[:PRECEDES {delta_t_ms: 650.0, sequence_type: "CAPTURE_THEN_QUERY"}]->(burst2)

// 4. [:PROFILES_AS] (NetworkBurst -> MetaActivity)
CREATE (burst1)-[:PROFILES_AS {confidence: 0.94, method: "flow_size_histogram"}]->(act1)
CREATE (burst2)-[:PROFILES_AS {confidence: 0.91, method: "sni_and_burst_shape"}]->(act2)
CREATE (burst3)-[:PROFILES_AS {confidence: 0.95, method: "telemetry_signature"}]->(act5)
CREATE (burst4)-[:PROFILES_AS {confidence: 0.98, method: "quic_bandwidth_tracker"}]->(act3)
CREATE (burst5)-[:PROFILES_AS {confidence: 0.42, method: "open_set_classifier"}]->(act4)
CREATE (burst6)-[:PROFILES_AS {confidence: 0.99, method: "heartbeat_profiler"}]->(act5)

// 5. [:GOVERNED_BY] (DetectedEntity -> CompliancePolicy)
CREATE (ent1)-[:GOVERNED_BY {scope: "Academic Integrity Evaluation"}]->(pol1)
CREATE (ent2)-[:GOVERNED_BY {scope: "Biometric Data Protection"}]->(pol2)
CREATE (ent2)-[:GOVERNED_BY {scope: "Bystander Consent Taxonomy"}]->(pol3)
CREATE (ent3)-[:GOVERNED_BY {scope: "Vehicle Identifier Obfuscation"}]->(pol3)
CREATE (ent4)-[:GOVERNED_BY {scope: "Corporate Trade Secret Perimeter"}]->(pol4)

// 6. [:EVALUATED_AGAINST] (MetaActivity -> CompliancePolicy)
CREATE (act1)-[:EVALUATED_AGAINST {environment: "Exam Room", risk_level: "HIGH"}]->(pol1)
CREATE (act2)-[:EVALUATED_AGAINST {environment: "Exam Room", risk_level: "CRITICAL"}]->(pol1)
CREATE (act3)-[:EVALUATED_AGAINST {environment: "Cleanroom Lab", risk_level: "CRITICAL"}]->(pol4)
CREATE (act4)-[:EVALUATED_AGAINST {environment: "Audited Zone", risk_level: "UNCERTAIN"}]->(pol5)
CREATE (act5)-[:EVALUATED_AGAINST {environment: "Standard Operation", risk_level: "LOW"}]->(pol6)

// 7. [:DICTATES] (CompliancePolicy -> ActionGateVerdict)
CREATE (pol1)-[:DICTATES {enforcement: "Automated ActionGate Intercept"}]->(vrd1)
CREATE (pol2)-[:DICTATES {enforcement: "Automated ActionGate Permitted"}]->(vrd2)
CREATE (pol3)-[:DICTATES {enforcement: "Automated ActionGate Permitted"}]->(vrd2)
CREATE (pol4)-[:DICTATES {enforcement: "Automated ActionGate Intercept"}]->(vrd3)
CREATE (pol5)-[:DICTATES {enforcement: "Proctor Review Required"}]->(vrd4)
CREATE (pol6)-[:DICTATES {enforcement: "Automated ActionGate Permitted"}]->(vrd5)

// 8. [:MITIGATED_BY] (DetectedEntity -> MitigationAction)
CREATE (ent2)-[:MITIGATED_BY {status: "APPLIED_ON_DEVICE", latency_ms: 21.4}]->(mit2)
CREATE (ent3)-[:MITIGATED_BY {status: "APPLIED_ON_DEVICE", latency_ms: 18.2}]->(mit3)

// 9. [:TRIGGERS_ACTION] (ActionGateVerdict -> MitigationAction)
CREATE (vrd1)-[:TRIGGERS_ACTION {priority: "IMMEDIATE_BLOCK"}]->(mit1)
CREATE (vrd2)-[:TRIGGERS_ACTION {priority: "PERMITTED_AUDIT"}]->(mit6)
CREATE (vrd3)-[:TRIGGERS_ACTION {priority: "IMMEDIATE_BLOCK"}]->(mit4)
CREATE (vrd4)-[:TRIGGERS_ACTION {priority: "ESCALATE_HUMAN"}]->(mit5)
CREATE (vrd5)-[:TRIGGERS_ACTION {priority: "PERMITTED_AUDIT"}]->(mit6)

// 10. GRAPHRAG DIRECT EVIDENCE BACK-LINKS (ActionGateVerdict -> Evidence Nodes)
// These bidirectional edges allow GraphRAG to retrieve grounded causal context in 1 hop!
CREATE (vrd1)-[:GROUNDED_IN {causal_factor: "Unredacted exam document capture"}]->(obs1)
CREATE (vrd1)-[:CORROBORATED_BY {causal_factor: "Exfiltration photo burst"}]->(burst1)
CREATE (vrd1)-[:CORROBORATED_BY {causal_factor: "Subsequent LLM vision prompt burst"}]->(burst2)
CREATE (vrd1)-[:CITES_POLICY {authority: "Institutional Honor Code"}]->(pol1)

CREATE (vrd2)-[:GROUNDED_IN {causal_factor: "Localized pedestrian face & plate"}]->(obs2)
CREATE (vrd2)-[:CORROBORATED_BY {causal_factor: "Benign telemetry sync burst"}]->(burst3)
CREATE (vrd2)-[:CITES_POLICY {authority: "EU GDPR & SITARA"}]->(pol2)
CREATE (vrd2)-[:CITES_POLICY {authority: "EU GDPR & SITARA"}]->(pol3)

CREATE (vrd3)-[:GROUNDED_IN {causal_factor: "Proprietary cleanroom screen display"}]->(obs3)
CREATE (vrd3)-[:CORROBORATED_BY {causal_factor: "512KB continuous video stream burst"}]->(burst4)
CREATE (vrd3)-[:CITES_POLICY {authority: "Facility Security Directive"}]->(pol4)

CREATE (vrd4)-[:GROUNDED_IN {causal_factor: "Ambiguous waveguide trigger"}]->(obs4)
CREATE (vrd4)-[:CORROBORATED_BY {causal_factor: "Adversarial jitter burst"}]->(burst5)
CREATE (vrd4)-[:CITES_POLICY {authority: "Calibrated Abstention Standard"}]->(pol5)

CREATE (vrd5)-[:GROUNDED_IN {causal_factor: "Idle standby BLE daemon"}]->(obs5)
CREATE (vrd5)-[:CORROBORATED_BY {causal_factor: "1KB periodic mTLS heartbeat"}]->(burst6)
CREATE (vrd5)-[:CITES_POLICY {authority: "Wearable Specification Standard"}]->(pol6);

// ==============================================================================
// STEP 4: GRAPHRAG DEMONSTRATION RETRIEVAL QUERIES
// ==============================================================================

// --- QUERY 1: BASIC RETRIEVAL (Fulltext Search on Policies) ---
// Retrieves policy requirements and mandated actions using natural language keywords:
// CALL db.index.fulltext.queryNodes("rag_policy_fulltext", "GDPR biometric face redaction") 
// YIELD node, score 
// RETURN node.policy_id AS PolicyID, node.title AS Title, node.mandated_action AS Mandate, node.rag_summary AS Summary, score
// ORDER BY score DESC LIMIT 3;

// --- QUERY 2: MULTI-HOP DEFENSIVE REASONING AUDIT (EXAM VIOLATION CHAIN) ---
// Retrieves the complete causal chain from Verdict -> Bursts -> Sensor -> Mitigation:
// MATCH (v:ActionGateVerdict {verdict_id: "VRD-EXAM-BLOCK-01"})
// MATCH (v)-[:GROUNDED_IN]->(obs:SensorObservation)
// MATCH (obs)-[:DETECTED]->(entity:DetectedEntity)
// MATCH (v)-[:CORROBORATED_BY]->(b:NetworkBurst)
// MATCH (b)-[:PROFILES_AS]->(act:MetaActivity)
// MATCH (v)-[:CITES_POLICY]->(pol:CompliancePolicy)
// MATCH (v)-[:TRIGGERS_ACTION]->(mit:MitigationAction)
// RETURN v.verdict_id AS Verdict, 
//        v.status AS GateStatus,
//        obs.obs_id AS SensorEvidence,
//        entity.category AS DetectedContent,
//        collect(DISTINCT b.burst_id) AS CorroboratingBursts,
//        collect(DISTINCT act.activity_type) AS InferredActivities,
//        pol.title AS ViolatedPolicy,
//        mit.name AS ExecutedMitigation;

// --- QUERY 3: DATA ANALYTICS & MITIGATION AUDIT ---
// Aggregates total network volume, average mitigation latency, and risk distribution across all scenarios:
// MATCH (b:NetworkBurst)-[:PROFILES_AS]->(act:MetaActivity)
// MATCH (v:ActionGateVerdict)-[:CORROBORATED_BY]->(b)
// OPTIONAL MATCH (v)-[:TRIGGERS_ACTION]->(mit:MitigationAction)
// RETURN act.risk_category AS RiskCategory,
//        count(DISTINCT b) AS BurstCount,
//        sum(b.total_bytes) AS TotalBytesTransmitted,
//        avg(mit.latency_ms) AS AvgMitigationLatencyMs,
//        collect(DISTINCT v.status) AS ActionGateVerdicts;
