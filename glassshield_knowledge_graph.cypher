// ==============================================================================
// GlassShield 🛡️🕶️ Knowledge Graph (Neo4j Cypher Script)
// Course: CS 5542 - Challenge 3: AI Design - Knowledge Graph with Neo4j
// Author: Vien (Vince) Nguyen
//
// HOW TO RUN IN NEO4J BROWSER / AURADB:
// 1. Open your Neo4j AuraDB web console (or Neo4j Browser).
// 2. You can execute this script in sections:
//    - Step 1: Run the Schema Constraints block.
//    - Step 2: Run the Ingest / CREATE block (creates 25 nodes and 27 edges).
//    - Step 3: Run the Demonstration Queries at the bottom to visualize the graph!
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

CREATE INDEX idx_obs_timestamp IF NOT EXISTS FOR (o:SensorObservation) ON (o.timestamp_iso);
CREATE INDEX idx_activity_type IF NOT EXISTS FOR (a:MetaActivity) ON (a.activity_type);
CREATE INDEX idx_verdict_status IF NOT EXISTS FOR (v:ActionGateVerdict) ON (v.status);

// ------------------------------------------------------------------------------
// STEP 2: KNOWLEDGE GRAPH DATA INGESTION
// Creates 25 Nodes and 27 Relationships across 5 GlassShield Scenarios:
// Scenario 1: Academic Exam Violation (Photo -> LLM Query -> Block)
// Scenario 2: Public Street Bystander Face Privacy (EgoBlur Mask -> GDPR -> Allow)
// Scenario 3: Secure Cleanroom IP Protection (Video Stream -> Lab Policy -> Block)
// Scenario 4: Adversarial Jitter & Abstention (Ambiguous Burst -> Unknown -> Confirm)
// Scenario 5: Benign Background Sync (Telemetry Upload -> Allow)
// ------------------------------------------------------------------------------

// --- 1. SENSOR OBSERVATIONS (W3C SOSA/SSN Grounding) ---
CREATE (obs1:SensorObservation {
    obs_id: "OBS-2026-EXAM-01",
    timestamp_iso: "2026-10-09T14:32:01.120Z",
    source_sensor: "RGB_CAMERA_1264x1264",
    frame_index: 104,
    device_model: "Ray-Ban Meta Gen2",
    optical_presence_verified: true
})
CREATE (obs2:SensorObservation {
    obs_id: "OBS-2026-STREET-02",
    timestamp_iso: "2026-10-09T15:10:22.450Z",
    source_sensor: "RGB_CAMERA_1264x1264",
    frame_index: 665,
    device_model: "Ray-Ban Meta Gen2",
    optical_presence_verified: true
})
CREATE (obs3:SensorObservation {
    obs_id: "OBS-2026-LAB-03",
    timestamp_iso: "2026-10-09T16:04:15.800Z",
    source_sensor: "RGB_CAMERA_1264x1264",
    frame_index: 1200,
    device_model: "Project Aria",
    optical_presence_verified: true
})
CREATE (obs4:SensorObservation {
    obs_id: "OBS-2026-AUDIT-04",
    timestamp_iso: "2026-10-09T16:45:00.210Z",
    source_sensor: "OPTICAL_WAVEGUIDE",
    frame_index: 2301,
    device_model: "Ray-Ban Meta Gen2",
    optical_presence_verified: true
})
CREATE (obs5:SensorObservation {
    obs_id: "OBS-2026-SYNC-05",
    timestamp_iso: "2026-10-09T17:00:00.000Z",
    source_sensor: "COMPANION_BLE_DAEMON",
    frame_index: 0,
    device_model: "Ray-Ban Meta Gen2",
    optical_presence_verified: false
})

// --- 2. DETECTED ENTITIES (W3C DPV / EgoBlur Detections) ---
CREATE (ent1:DetectedEntity {
    entity_id: "ENT-EXAM-DOC-01",
    category: "DOCUMENT_EXAM_TEXT",
    confidence: 0.942,
    bbox: [120, 310, 540, 890],
    area_percentage: 24.5,
    redaction_applied: false,
    redaction_type: "NONE"
})
CREATE (ent2:DetectedEntity {
    entity_id: "ENT-STREET-FACE-01",
    category: "FACE",
    confidence: 0.965,
    bbox: [154, 443, 562, 673],
    area_percentage: 8.7,
    redaction_applied: true,
    redaction_type: "GAUSSIAN_BLUR"
})
CREATE (ent3:DetectedEntity {
    entity_id: "ENT-STREET-LP-02",
    category: "LICENSE_PLATE",
    confidence: 0.912,
    bbox: [620, 810, 680, 950],
    area_percentage: 2.1,
    redaction_applied: true,
    redaction_type: "SOLID_MASK"
})
CREATE (ent4:DetectedEntity {
    entity_id: "ENT-LAB-SCREEN-01",
    category: "PROPRIETARY_DISPLAY",
    confidence: 0.887,
    bbox: [50, 100, 700, 1100],
    area_percentage: 42.0,
    redaction_applied: false,
    redaction_type: "NONE"
})

// --- 3. NETWORK BURSTS (OASIS STIX / OVRseen Flow Profiling) ---
CREATE (burst1:NetworkBurst {
    burst_id: "BURST-EXAM-PHOTO-01",
    timestamp_iso: "2026-10-09T14:32:01.240Z",
    direction: "UPLINK",
    total_bytes: 49152,
    packet_count: 38,
    duration_ms: 185.0,
    mean_inter_arrival_ms: 4.8
})
CREATE (burst2:NetworkBurst {
    burst_id: "BURST-EXAM-LLM-02",
    timestamp_iso: "2026-10-09T14:32:01.890Z",
    direction: "UPLINK",
    total_bytes: 12288,
    packet_count: 14,
    duration_ms: 92.0,
    mean_inter_arrival_ms: 6.5
})
CREATE (burst3:NetworkBurst {
    burst_id: "BURST-STREET-SYNC-01",
    timestamp_iso: "2026-10-09T15:10:22.580Z",
    direction: "UPLINK",
    total_bytes: 4096,
    packet_count: 5,
    duration_ms: 45.0,
    mean_inter_arrival_ms: 9.0
})
CREATE (burst4:NetworkBurst {
    burst_id: "BURST-LAB-STREAM-01",
    timestamp_iso: "2026-10-09T16:04:15.910Z",
    direction: "UPLINK",
    total_bytes: 524288,
    packet_count: 412,
    duration_ms: 1020.0,
    mean_inter_arrival_ms: 2.4
})
CREATE (burst5:NetworkBurst {
    burst_id: "BURST-JITTER-AMBIG-01",
    timestamp_iso: "2026-10-09T16:45:00.320Z",
    direction: "BIDIRECTIONAL",
    total_bytes: 18432,
    packet_count: 22,
    duration_ms: 310.0,
    mean_inter_arrival_ms: 14.1
})
CREATE (burst6:NetworkBurst {
    burst_id: "BURST-SYS-HEARTBEAT-01",
    timestamp_iso: "2026-10-09T17:00:00.080Z",
    direction: "BIDIRECTIONAL",
    total_bytes: 1024,
    packet_count: 2,
    duration_ms: 12.0,
    mean_inter_arrival_ms: 6.0
})

// --- 4. META ACTIVITIES (Behavioral Operational States) ---
CREATE (act1:MetaActivity {
    activity_id: "ACT-PHOTO-CAPTURE",
    activity_type: "PHOTO",
    confidence: 0.94,
    is_open_set_abstention: false,
    protocol_inferred: "HTTPS/TLS1.3"
})
CREATE (act2:MetaActivity {
    activity_id: "ACT-AI-QUERY",
    activity_type: "AI_INTERACTION",
    confidence: 0.91,
    is_open_set_abstention: false,
    protocol_inferred: "HTTPS/TLS1.3"
})
CREATE (act3:MetaActivity {
    activity_id: "ACT-VIDEO-STREAM",
    activity_type: "VIDEO_STREAM",
    confidence: 0.98,
    is_open_set_abstention: false,
    protocol_inferred: "QUIC/UDP"
})
CREATE (act4:MetaActivity {
    activity_id: "ACT-ABSTAIN-UNKNOWN",
    activity_type: "UNKNOWN",
    confidence: 0.42,
    is_open_set_abstention: true,
    protocol_inferred: "BLE_L2CAP"
})
CREATE (act5:MetaActivity {
    activity_id: "ACT-DEVICE-SYNC",
    activity_type: "SYNC_UPLOAD",
    confidence: 0.95,
    is_open_set_abstention: false,
    protocol_inferred: "HTTPS/TLS1.3"
})

// --- 5. COMPLIANCE POLICIES (Regulatory & Institutional Rules) ---
CREATE (pol1:CompliancePolicy {
    policy_id: "POL-EXAM-3.2",
    title: "Prohibition of Electronic Assistance and Capture During Evaluation",
    jurisdiction: "Institutional Academic Council",
    mandated_action: "BLOCK_AND_FLAG_PROCTOR",
    citation: "Sec 3.2.1 Unauthorized AI Inference"
})
CREATE (pol2:CompliancePolicy {
    policy_id: "POL-GDPR-ART9",
    title: "Processing of Special Categories of Personal Data (Biometric Facial Data)",
    jurisdiction: "European Union GDPR",
    mandated_action: "MANDATORY_ON_DEVICE_REDACTION",
    citation: "Article 9(1) Biometric Identification"
})
CREATE (pol3:CompliancePolicy {
    policy_id: "POL-SITARA-001",
    title: "SITARA Bystander Consent Taxonomy Tier 2",
    jurisdiction: "Smart Wearable Research (SYSNET-LUMS)",
    mandated_action: "MASK_NON_CONSENTING_BYSTANDERS",
    citation: "Sec 4.1 Incidental Capture"
})
CREATE (pol4:CompliancePolicy {
    policy_id: "POL-LAB-REC-01",
    title: "Corporate IP & Cleanroom Zero-Transmission Mandate",
    jurisdiction: "Advanced R&D Facility Security",
    mandated_action: "BLOCK_STREAM",
    citation: "Rule 12 Confidential IP"
})
CREATE (pol5:CompliancePolicy {
    policy_id: "POL-SITARA-UNCERTAIN",
    title: "Edge-Case Handling & Calibrated Abstention Standard",
    jurisdiction: "Smart Wearable Research (SYSNET-LUMS)",
    mandated_action: "FLAG_UNCERTAINTY",
    citation: "Sec 5.3 Ambiguous Flow Protocol"
})
CREATE (pol6:CompliancePolicy {
    policy_id: "POL-OPEN-SYNC-05",
    title: "Wearable Architecture Standard Device Telemetry Allowance",
    jurisdiction: "Global Default Standard",
    mandated_action: "ALLOW_BACKGROUND_SYNC",
    citation: "Sec 1.4 Heartbeat Protocol"
})

// --- 6. ACTION GATE VERDICTS (Enforceable Decision & Reason) ---
CREATE (vrd1:ActionGateVerdict {
    verdict_id: "VRD-EXAM-BLOCK-01",
    status: "BLOCK",
    uncertainty_score: 0.05,
    narrative_reasoning: "Observable burst sequence matches camera capture followed by cloud generative AI query during examination interval per POL-EXAM-3.2.",
    human_override: false
})
CREATE (vrd2:ActionGateVerdict {
    verdict_id: "VRD-STREET-ALLOW-02",
    status: "ALLOW",
    uncertainty_score: 0.04,
    narrative_reasoning: "Bystander facial biometrics localized and redacted on-device prior to storage. Complies with GDPR Art. 9 and SITARA Tier 2.",
    human_override: false
})
CREATE (vrd3:ActionGateVerdict {
    verdict_id: "VRD-LAB-BLOCK-03",
    status: "BLOCK",
    uncertainty_score: 0.02,
    narrative_reasoning: "Continuous high-throughput uplink video stream detected inside restricted cleanroom perimeter per POL-LAB-REC-01.",
    human_override: false
})
CREATE (vrd4:ActionGateVerdict {
    verdict_id: "VRD-JITTER-CONFIRM-04",
    status: "USER_CONFIRMATION_REQUIRED",
    uncertainty_score: 0.58,
    narrative_reasoning: "Burst profile confidence below calibrated threshold (42%). Model abstains to UNKNOWN; proctor confirmation required per POL-SITARA-UNCERTAIN.",
    human_override: false
})
CREATE (vrd5:ActionGateVerdict {
    verdict_id: "VRD-SYNC-ALLOW-05",
    status: "ALLOW",
    uncertainty_score: 0.01,
    narrative_reasoning: "Periodic background telemetry heartbeat verified with standard wearable profile per POL-OPEN-SYNC-05.",
    human_override: false
})

// ------------------------------------------------------------------------------
// CONNECTING RELATIONSHIPS (EDGES)
// ------------------------------------------------------------------------------

// 1. [:DETECTED] (Observation -> DetectedEntity)
CREATE (obs1)-[:DETECTED {detector: "egoblur_gen1_jit"}]->(ent1)
CREATE (obs2)-[:DETECTED {detector: "egoblur_gen1_jit"}]->(ent2)
CREATE (obs2)-[:DETECTED {detector: "egoblur_gen1_jit"}]->(ent3)
CREATE (obs3)-[:DETECTED {detector: "egoblur_gen1_jit"}]->(ent4)

// 2. [:TEMPORALLY_CORRELATED_WITH] (Observation -> NetworkBurst with delta_t_ms)
CREATE (obs1)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 120.0}]->(burst1)
CREATE (obs2)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 130.0}]->(burst3)
CREATE (obs3)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 110.0}]->(burst4)
CREATE (obs4)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 110.0}]->(burst5)
CREATE (obs5)-[:TEMPORALLY_CORRELATED_WITH {delta_t_ms: 80.0}]->(burst6)

// 3. [:PRECEDES] (Temporal sequence chaining between bursts)
CREATE (burst1)-[:PRECEDES {delta_t_ms: 650.0}]->(burst2)

// 4. [:PROFILES_AS] (NetworkBurst -> MetaActivity)
CREATE (burst1)-[:PROFILES_AS {confidence: 0.94}]->(act1)
CREATE (burst2)-[:PROFILES_AS {confidence: 0.91}]->(act2)
CREATE (burst3)-[:PROFILES_AS {confidence: 0.95}]->(act5)
CREATE (burst4)-[:PROFILES_AS {confidence: 0.98}]->(act3)
CREATE (burst5)-[:PROFILES_AS {confidence: 0.42}]->(act4)
CREATE (burst6)-[:PROFILES_AS {confidence: 0.99}]->(act5)

// 5. [:GOVERNED_BY] (DetectedEntity -> CompliancePolicy)
CREATE (ent1)-[:GOVERNED_BY {scope: "Academic Integrity"}]->(pol1)
CREATE (ent2)-[:GOVERNED_BY {scope: "Biometric Protection"}]->(pol2)
CREATE (ent2)-[:GOVERNED_BY {scope: "Bystander Consent"}]->(pol3)
CREATE (ent3)-[:GOVERNED_BY {scope: "Vehicle Identifier"}]->(pol3)
CREATE (ent4)-[:GOVERNED_BY {scope: "Corporate Trade Secret"}]->(pol4)

// 6. [:EVALUATED_AGAINST] (MetaActivity -> CompliancePolicy)
CREATE (act1)-[:EVALUATED_AGAINST {environment: "Exam Room"}]->(pol1)
CREATE (act2)-[:EVALUATED_AGAINST {environment: "Exam Room"}]->(pol1)
CREATE (act3)-[:EVALUATED_AGAINST {environment: "Secure Lab"}]->(pol4)
CREATE (act4)-[:EVALUATED_AGAINST {environment: "Audited Zone"}]->(pol5)
CREATE (act5)-[:EVALUATED_AGAINST {environment: "Standard Operations"}]->(pol6)

// 7. [:DICTATES] (CompliancePolicy -> ActionGateVerdict)
CREATE (pol1)-[:DICTATES {enforcement: "Automated ActionGate"}]->(vrd1)
CREATE (pol2)-[:DICTATES {enforcement: "Automated ActionGate"}]->(vrd2)
CREATE (pol3)-[:DICTATES {enforcement: "Automated ActionGate"}]->(vrd2)
CREATE (pol4)-[:DICTATES {enforcement: "Automated ActionGate"}]->(vrd3)
CREATE (pol5)-[:DICTATES {enforcement: "Proctor Review Required"}]->(vrd4)
CREATE (pol6)-[:DICTATES {enforcement: "Automated ActionGate"}]->(vrd5);


// ==============================================================================
// STEP 3: DEMONSTRATION & PROJECT-SPECIFIC CYPHER QUERIES
// (Use these for your PowerPoint slides and live in-class demonstration!)
// ==============================================================================

// --- QUERY 1: VISUALIZE FULL KNOWLEDGE GRAPH ---
// Shows all nodes and relationships on your screen.
// MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m;

// --- QUERY 2: MULTI-HOP DEFENSIVE REASONING AUDIT (EXAM VIOLATION CHAIN) ---
// Traces from a physical camera observation -> correlated uplink burst ->
// preceding LLM query -> evaluated policy -> blocking gate verdict.
// MATCH path = (obs:SensorObservation {obs_id: "OBS-2026-EXAM-01"})
//              -[:TEMPORALLY_CORRELATED_WITH]->(b1:NetworkBurst)
//              -[:PRECEDES]->(b2:NetworkBurst)
//              -[:PROFILES_AS]->(act:MetaActivity)
//              -[:EVALUATED_AGAINST]->(pol:CompliancePolicy)
//              -[:DICTATES]->(gate:ActionGateVerdict)
// RETURN path;

// --- QUERY 3: BYSTANDER PRIVACY & GDPR REDACTION AUDIT ---
// Finds all facial biometrics detected on the street, verifying that redaction
// was applied before policy evaluation and ALLOW verdict.
// MATCH (obs:SensorObservation)-[:DETECTED]->(entity:DetectedEntity {category: "FACE"})
// MATCH (entity)-[:GOVERNED_BY]->(pol:CompliancePolicy)
// MATCH (pol)-[:DICTATES]->(gate:ActionGateVerdict)
// RETURN obs.obs_id, entity.entity_id, entity.redaction_applied, entity.redaction_type, pol.title, gate.status;

// --- QUERY 4: CALIBRATED OPEN-SET ABSTENTION (UNKNOWN) ---
// Finds bursts where model was uncertain, proving that the system abstained to
// UNKNOWN and demanded human proctor confirmation rather than making a false accusation.
// MATCH (burst:NetworkBurst)-[:PROFILES_AS]->(act:MetaActivity {activity_type: "UNKNOWN"})
// MATCH (act)-[:EVALUATED_AGAINST]->(pol:CompliancePolicy)
// MATCH (pol)-[:DICTATES]->(gate:ActionGateVerdict {status: "USER_CONFIRMATION_REQUIRED"})
// RETURN burst.burst_id, burst.total_bytes, act.confidence, gate.narrative_reasoning;
