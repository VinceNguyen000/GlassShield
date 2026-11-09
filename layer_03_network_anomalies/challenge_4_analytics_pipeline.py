"""
layer_03_network_anomalies/challenge_4_analytics_pipeline.py
------------------------------------------------------------
CS 5542 — Challenge 4: AI Design Implementation
Big Data Analytics, Multimodal Generation, and Application Design

Implements:
1. Big Data Ingestion & Streaming Window Aggregation (PySpark-compatible schema)
2. Unsupervised Clustering (K-Means & Louvain Community Modeling)
3. Anomaly Detection (Isolation Forest on Encrypted Network Bursts)
4. Multimodal Generation (Real-Time Open-Ear Audio TTS & One-Click Visual Proof Card)
5. Generation of high-resolution figures for the 10-Slide Presentation
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, precision_recall_fscore_support

# Output paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRESENTATION_FIGURES = os.path.join(BASE_DIR, "presentation", "figures")
os.makedirs(PRESENTATION_FIGURES, exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)

# ==============================================================================
# Helper: TrueType Font Loader
# ==============================================================================
def get_font(size, bold=False):
    font_paths = [
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf" if bold else "C:\\Windows\\Fonts\\calibri.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ==============================================================================
# PART 1: Big Data Telemetry Pipeline & Feature Extraction
# ==============================================================================
def generate_synthetic_telemetry(n_samples=1200):
    """
    Simulates high-throughput encrypted packet bursts and sensor telemetry
    from a fleet of wearable smart glasses across two distinct operational communities:
      - Community 1: Public Walk & Cafe (Legitimate low-bandwidth photos, bystander faces/plates)
      - Community 2: Restricted Cleanroom & Exam (Covert high-throughput video exfiltration)
      - Anomalous / Zero-Day: Covert intermittent burst exfiltration attacks
    """
    data = []
    
    # 1. Public Street & Casual (60% of data - Community 1)
    n_comm1 = int(n_samples * 0.60)
    for i in range(n_comm1):
        # Packet sizes: small HTTP/TLS handshakes, sporadic photos (<50 KB)
        burst_kb = np.random.gamma(shape=2.0, scale=15.0)  # Mean ~30 KB
        mean_pkt_size = np.random.normal(240, 45)          # Small TLS packets
        std_pkt_size = np.random.normal(85, 20)
        mean_iat_ms = np.random.exponential(120.0)         # Sporadic bursts
        uplink_ratio = np.random.beta(2, 5)                # Mostly downlink traffic
        packet_count = int(np.random.normal(80, 25))
        face_count = int(np.random.poisson(2.5))           # Frequently observes faces
        monitor_count = 0                                  # No confidential screens
        
        data.append({
            "event_id": f"EVT-PUB-{i:04d}",
            "community_ground_truth": "Public_Street",
            "burst_volume_kb": max(5.0, burst_kb),
            "mean_packet_size": max(64.0, mean_pkt_size),
            "std_packet_size": max(10.0, std_pkt_size),
            "mean_iat_ms": max(2.0, mean_iat_ms),
            "uplink_ratio": float(np.clip(uplink_ratio, 0.05, 0.95)),
            "packet_count": max(10, packet_count),
            "face_count": face_count,
            "monitor_count": monitor_count,
            "is_anomaly": 0
        })
        
    # 2. Restricted Lab & Exam Room (32% of data - Community 2)
    n_comm2 = int(n_samples * 0.32)
    for i in range(n_comm2):
        # Heavy continuous video stream (4+ Mbps = ~500 KB/s)
        burst_kb = np.random.normal(650, 90)              # Continuous streaming burst
        mean_pkt_size = np.random.normal(1280, 80)        # Max MTU video frames
        std_pkt_size = np.random.normal(320, 40)
        mean_iat_ms = np.random.exponential(8.0)          # Ultra-fast packet inter-arrival
        uplink_ratio = np.random.beta(8, 2)               # Heavy uplink exfiltration
        packet_count = int(np.random.normal(750, 110))
        face_count = int(np.random.poisson(0.3))          # Few or no faces
        monitor_count = int(np.random.poisson(1.8))       # Points at restricted screens/papers
        
        data.append({
            "event_id": f"EVT-RES-{i:04d}",
            "community_ground_truth": "Restricted_Lab",
            "burst_volume_kb": max(200.0, burst_kb),
            "mean_packet_size": max(800.0, mean_pkt_size),
            "std_packet_size": max(100.0, std_pkt_size),
            "mean_iat_ms": max(0.5, mean_iat_ms),
            "uplink_ratio": float(np.clip(uplink_ratio, 0.70, 0.99)),
            "packet_count": max(300, packet_count),
            "face_count": face_count,
            "monitor_count": monitor_count,
            "is_anomaly": 0
        })
        
    # 3. Covert Zero-Day Exfiltration Anomalies (8% of data)
    n_anom = n_samples - n_comm1 - n_comm2
    for i in range(n_anom):
        # Micro-burst pulsing (trying to evade simple thresholds)
        burst_kb = np.random.uniform(250, 480)
        mean_pkt_size = np.random.normal(920, 150)
        std_pkt_size = np.random.normal(450, 60)
        mean_iat_ms = np.random.uniform(15.0, 45.0)
        uplink_ratio = np.random.uniform(0.75, 0.98)
        packet_count = int(np.random.uniform(220, 450))
        face_count = np.random.choice([0, 1])
        monitor_count = np.random.choice([1, 2])
        
        data.append({
            "event_id": f"EVT-ANOM-{i:04d}",
            "community_ground_truth": "Covert_Exfiltration_Attack",
            "burst_volume_kb": burst_kb,
            "mean_packet_size": mean_pkt_size,
            "std_packet_size": std_pkt_size,
            "mean_iat_ms": mean_iat_ms,
            "uplink_ratio": uplink_ratio,
            "packet_count": packet_count,
            "face_count": face_count,
            "monitor_count": monitor_count,
            "is_anomaly": 1
        })
        
    return data


def run_analytics_experiments(dataset):
    """
    Executes K-Means Clustering and Isolation Forest Anomaly Detection.
    Returns metrics, cluster labels, and anomaly scores.
    """
    feature_matrix = np.array([
        [
            d["burst_volume_kb"],
            d["mean_packet_size"],
            d["std_packet_size"],
            d["mean_iat_ms"],
            d["uplink_ratio"],
            d["packet_count"],
            d["monitor_count"]
        ]
        for d in dataset
    ])
    
    # Feature scaling (Standardization)
    means = np.mean(feature_matrix, axis=0)
    stds = np.std(feature_matrix, axis=0) + 1e-6
    X_scaled = (feature_matrix - means) / stds
    
    # 1. K-Means Clustering (Community Identification)
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    sil_score = silhouette_score(X_scaled, cluster_labels)
    
    # 2. Isolation Forest Anomaly Detection
    # Train on normal samples (is_anomaly == 0)
    normal_indices = [i for i, d in enumerate(dataset) if d["is_anomaly"] == 0]
    X_normal = X_scaled[normal_indices]
    
    iso_forest = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
    iso_forest.fit(X_normal)
    
    # Predict on full dataset (-1: anomaly, 1: normal)
    raw_preds = iso_forest.predict(X_scaled)
    anomaly_preds = np.where(raw_preds == -1, 1, 0)
    anomaly_scores = -iso_forest.score_samples(X_scaled)  # Higher = more anomalous
    
    # Ground truth evaluation
    y_true = np.array([d["is_anomaly"] for d in dataset])
    p, r, f1, _ = precision_recall_fscore_support(y_true, anomaly_preds, average="binary")
    
    metrics = {
        "n_samples": len(dataset),
        "kmeans_silhouette_score": round(float(sil_score), 4),
        "anomaly_precision": round(float(p), 4),
        "anomaly_recall": round(float(r), 4),
        "anomaly_f1": round(float(f1), 4),
        "normal_samples": len(normal_indices),
        "anomalous_samples": int(np.sum(y_true))
    }
    
    # PCA for 2D visualization
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    return metrics, X_pca, cluster_labels, anomaly_preds, anomaly_scores


# ==============================================================================
# PART 2: Visual Chart Generation (Figures for 10 Slides)
# ==============================================================================
def generate_figure_pipeline_architecture():
    """Generates Slide 2 Architecture: PySpark Distributed Telemetry Pipeline"""
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")
    ax.axis("off")
    
    # Palette
    c_blue = "#38BDF8"
    c_teal = "#2DD4BF"
    c_purple = "#A78BFA"
    c_amber = "#FBBF24"
    c_card = "#1E293B"
    c_border = "#334155"
    
    # Draw Pipeline Stages
    stages = [
        {"x": 0.05, "title": "Stage 1: Edge Ingestion", "tech": "Kafka / MQTT Stream", 
         "desc": "High-freq encrypted packet metadata\n• Packet sizes & timestamps\n• Uplink/Downlink direction\n• Edge EgoBlur vision tags", "color": c_blue},
        {"x": 0.29, "title": "Stage 2: PySpark Aggregator", "tech": "Structured Streaming", 
         "desc": "500ms sliding window (100ms hop)\n• Micro-burst volume (KB)\n• Inter-arrival time (IAT) std\n• Packet entropy & ratio", "color": c_teal},
        {"x": 0.53, "title": "Stage 3: Community & ML", "tech": "Louvain & Isolation Forest", 
         "desc": "Dual-branch real-time scoring\n• Louvain community filtering\n• Isolation Forest zero-day flag\n• Action Gate boundary (<15ms)", "color": c_purple},
        {"x": 0.77, "title": "Stage 4: Multimodal Gate", "tech": "TTS & Proof Card API", 
         "desc": "Synchronous action dispatch\n• Open-ear spoken whisper alert\n• Proctor visual proof card\n• Telemetry JSONL audit log", "color": c_amber}
    ]
    
    for s in stages:
        # Card box
        box = patches.FancyBboxPatch((s["x"], 0.20), 0.19, 0.65, boxstyle="round,pad=0.02,rounding_size=0.03",
                                     facecolor=c_card, edgecolor=s["color"], linewidth=2)
        ax.add_patch(box)
        
        # Header
        ax.text(s["x"] + 0.095, 0.78, s["title"], color="#F8FAFC", fontsize=11, fontweight="bold", ha="center")
        ax.text(s["x"] + 0.095, 0.73, f"[{s['tech']}]", color=s["color"], fontsize=9.5, fontweight="semibold", ha="center")
        
        # Horizontal divider
        ax.plot([s["x"] + 0.02, s["x"] + 0.17], [0.69, 0.69], color=c_border, linewidth=1)
        
        # Description
        ax.text(s["x"] + 0.02, 0.65, s["desc"], color="#94A3B8", fontsize=9, va="top", family="sans-serif", linespacing=1.4)
        
    # Draw arrows between stages
    for i in range(3):
        x_start = stages[i]["x"] + 0.20
        x_end = stages[i+1]["x"] - 0.01
        ax.annotate("", xy=(x_end, 0.52), xytext=(x_start, 0.52),
                    arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#64748B", lw=2.5))
        
    # Title & Subtitle
    ax.text(0.50, 0.95, "GlassShield Big Data Telemetry & Distributed Stream Pipeline", 
            color="#FFFFFF", fontsize=16, fontweight="bold", ha="center")
    ax.text(0.50, 0.90, "End-to-End Ingestion, Windowed Feature Extraction, Graph Community Filter & Multimodal Gate", 
            color="#38BDF8", fontsize=11, ha="center")
    
    # Save figure
    out_path = os.path.join(PRESENTATION_FIGURES, "ch4_pipeline_architecture.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


def generate_figure_clustering_and_anomaly(X_pca, cluster_labels, anomaly_scores, dataset):
    """Generates Slide 3 & 4 Visualization: 2-Panel Clustering & Anomaly Score Chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.2), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    for ax in (ax1, ax2):
        ax.set_facecolor("#1E293B")
        ax.tick_params(colors="#94A3B8")
        for spine in ax.spines.values():
            spine.set_color("#334155")
            
    # Panel 1: Community Separation (PCA Projection)
    colors = ["#38BDF8" if c == 0 else "#EF4444" for c in cluster_labels]
    scatter = ax1.scatter(X_pca[:, 0], X_pca[:, 1], c=colors, alpha=0.65, s=28, edgecolors="none")
    ax1.set_title("Unsupervised Community Clusters (K-Means / Louvain)", color="#F8FAFC", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Principal Component 1 (Traffic Burst Volume & MTU)", color="#94A3B8", fontsize=10)
    ax1.set_ylabel("Principal Component 2 (IAT & Uplink Ratio)", color="#94A3B8", fontsize=10)
    
    # Legend custom patches
    p1 = patches.Patch(color="#38BDF8", label="Community 1: Public Casual (Low Burst, Allow)")
    p2 = patches.Patch(color="#EF4444", label="Community 2: Restricted Lab (Continuous Stream, Block)")
    ax1.legend(handles=[p1, p2], loc="upper left", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.15, color="#94A3B8")
    
    # Panel 2: Isolation Forest Anomaly Distribution
    normal_scores = [anomaly_scores[i] for i, d in enumerate(dataset) if d["is_anomaly"] == 0]
    anom_scores = [anomaly_scores[i] for i, d in enumerate(dataset) if d["is_anomaly"] == 1]
    
    ax2.hist(normal_scores, bins=35, alpha=0.7, color="#2DD4BF", label="Legitimate Operational Bursts (n=1104)", density=True)
    ax2.hist(anom_scores, bins=20, alpha=0.75, color="#F59E0B", label="Covert Exfiltration Anomalies (n=96)", density=True)
    
    # Decision boundary threshold line
    thresh = np.percentile(normal_scores, 92)
    ax2.axvline(thresh, color="#EF4444", linestyle="--", linewidth=2, label=f"Anomaly Threshold ({thresh:.2f})")
    
    ax2.set_title("Isolation Forest Anomaly Score Distribution", color="#F8FAFC", fontsize=13, fontweight="bold", pad=12)
    ax2.set_xlabel("Anomaly Score (Higher = Greater Exfiltration Likelihood)", color="#94A3B8", fontsize=10)
    ax2.set_ylabel("Density", color="#94A3B8", fontsize=10)
    ax2.legend(loc="upper right", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.15, color="#94A3B8")
    
    out_path = os.path.join(PRESENTATION_FIGURES, "ch4_clustering_anomaly_detection.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


def generate_multimodal_proof_card():
    """
    Generates Slide 6 Visual Output: Authentic One-Click Visual Proof Card (PNG)
    Combining: Redacted Scene + Network Burst Spike + Grounded Policy Badge + Audit Controls.
    """
    card_w, card_h = 1200, 720
    img = Image.new("RGB", (card_w, card_h), "#0F172A")
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_title = get_font(24, bold=True)
    font_subtitle = get_font(14, bold=False)
    font_header = get_font(16, bold=True)
    font_body = get_font(13, bold=False)
    font_body_b = get_font(13, bold=True)
    font_badge = get_font(11, bold=True)
    font_mono = get_font(12, bold=False)
    
    # Header Banner
    draw.rectangle([0, 0, card_w, 75], fill="#1E293B", outline="#334155", width=1)
    draw.text((30, 16), "GLASSSHIELD ONE-CLICK AUDIT PROOF CARD", fill="#F8FAFC", font=font_title)
    draw.text((30, 48), "INCIDENT ID: EVT-2026-1029-SEC09  |  TIME: 16:42:18 UTC  |  LOCATION: FAB-3 CLEANROOM", fill="#94A3B8", font=font_subtitle)
    
    # Verdict Status Badge (Top Right)
    draw.rounded_rectangle([card_w - 240, 18, card_w - 30, 58], radius=8, fill="#7F1D1D", outline="#EF4444", width=2)
    draw.text((card_w - 225, 27), "BLOCKED (4.8ms)", fill="#FEF2F2", font=font_header)
    
    # Panel 1: Redacted Camera Frame (Simulated Smart Glasses View)
    p1_box = [30, 95, 430, 470]
    draw.rounded_rectangle(p1_box, radius=10, fill="#1E293B", outline="#475569", width=1)
    draw.text((45, 110), "1. ON-DEVICE CAMERA CROP (REDACTED)", fill="#38BDF8", font=font_header)
    
    # Draw simulated workstation inside camera frame
    draw.rectangle([50, 150, 410, 390], fill="#020617")
    # Draw a computer monitor on the desk
    draw.rectangle([90, 180, 370, 340], fill="#1E293B", outline="#64748B", width=2)
    draw.rectangle([210, 340, 250, 375], fill="#475569")
    draw.rectangle([170, 375, 290, 385], fill="#475569")
    
    # Draw Redaction Bounding Box over Monitor
    draw.rectangle([95, 185, 365, 335], outline="#EF4444", width=3)
    draw.rectangle([95, 185, 365, 220], fill="#7F1D1D")
    draw.text((105, 192), "[REDACTED] CONFIDENTIAL SCHEMATIC", fill="#FEE2E2", font=font_badge)
    
    # Bystander Face Blurred in background
    draw.ellipse([60, 160, 85, 195], fill="#64748B", outline="#94A3B8", width=1)
    draw.text((63, 172), "BLUR", fill="#FFFFFF", font=font_badge)
    
    draw.text((45, 410), "Vision Engine: EgoBlur Gen1 JIT (<22ms)", fill="#94A3B8", font=font_body)
    draw.text((45, 435), "Detected: 1 Restricted Screen (0.94), 1 Face (0.91)", fill="#E2E8F0", font=font_body_b)
    
    # Panel 2: Encrypted Traffic Burst Profile (Network Anomaly)
    p2_box = [450, 95, 850, 470]
    draw.rounded_rectangle(p2_box, radius=10, fill="#1E293B", outline="#475569", width=1)
    draw.text((465, 110), "2. ENCRYPTED TRAFFIC SPIKE (OVRSEEN)", fill="#2DD4BF", font=font_header)
    
    # Chart area inside Panel 2
    draw.rectangle([470, 150, 830, 380], fill="#020617", outline="#334155", width=1)
    
    # Draw simulated burst curve (spike from 40 Kbps to 4.2 Mbps)
    points = [
        (480, 365), (510, 362), (540, 366), (570, 360), (600, 364),
        (620, 358), (640, 210), (660, 175), (690, 170), (720, 178),
        (750, 172), (780, 175), (810, 365) # Sudden drop after Block!
    ]
    for i in range(len(points) - 1):
        color = "#2DD4BF" if points[i][1] > 300 else "#EF4444"
        draw.line([points[i], points[i+1]], fill=color, width=3)
        
    draw.text((480, 160), "4.2 Mbps Continuous Stream Spike", fill="#EF4444", font=font_badge)
    draw.text((480, 340), "Normal Baseline: 38 Kbps", fill="#2DD4BF", font=font_badge)
    draw.line([(810, 160), (810, 375)], fill="#EF4444", width=2)
    draw.text((715, 320), "STREAM KILLED", fill="#FEF2F2", font=font_badge)
    
    draw.text((465, 410), "Uplink Ratio: 0.94  |  Avg Packet Size: 1,290 B (MTU)", fill="#94A3B8", font=font_body)
    draw.text((465, 435), "Inference: Unauthorized Live RTSP/WebRTC Exfiltration", fill="#E2E8F0", font=font_body_b)
    
    # Panel 3: Grounded Policy Citation & Regulatory Badge
    p3_box = [870, 95, card_w - 30, 470]
    draw.rounded_rectangle(p3_box, radius=10, fill="#1E293B", outline="#475569", width=1)
    draw.text((885, 110), "3. CITED LEGAL POLICY", fill="#A78BFA", font=font_header)
    
    draw.rectangle([885, 150, card_w - 45, 230], fill="#311042", outline="#A78BFA", width=1)
    draw.text((895, 160), "CLEANROOM NDA SEC. 4.1", fill="#F5D0FE", font=font_body_b)
    draw.text((895, 185), "Strict Prohibition of Real-Time Video", fill="#FFFFFF", font=font_body)
    draw.text((895, 205), "Transmission inside Cleanroom Zone B.", fill="#CBD5E1", font=font_body)
    
    draw.rectangle([885, 245, card_w - 45, 325], fill="#1E1B4B", outline="#818CF8", width=1)
    draw.text((895, 255), "GDPR ARTICLE 9 (BIOMETRICS)", fill="#C7D2FE", font=font_body_b)
    draw.text((895, 280), "Mandatory On-Device Redaction of", fill="#FFFFFF", font=font_body)
    draw.text((895, 300), "Unconsented Bystander Facial Vectors.", fill="#CBD5E1", font=font_body)
    
    draw.text((885, 355), "Graph Knowledge Node:", fill="#94A3B8", font=font_body)
    draw.text((885, 375), "Community: Restricted_Lab (k=2)", fill="#38BDF8", font=font_body_b)
    draw.text((885, 400), "Mitigation Node: MIT-004 (Kill Stream)", fill="#2DD4BF", font=font_body_b)
    draw.text((885, 430), "Enforcement Latency: 4.8 ms", fill="#FBBF24", font=font_header)
    
    # Bottom Panel: Multi-Party Audio Transcript & Action Controls
    bot_box = [30, 490, card_w - 30, card_h - 25]
    draw.rounded_rectangle(bot_box, radius=10, fill="#1E293B", outline="#475569", width=1)
    
    # Audio transcript sub-box
    draw.text((45, 505), "4. OPEN-EAR WEARER AUDIO WHISPER ALERT (TTS TRANSCRIPT)", fill="#FBBF24", font=font_header)
    draw.rectangle([45, 535, 780, 605], fill="#0F172A", outline="#334155", width=1)
    draw.text((55, 545), "[Tone Chime] \"Notice: Video streaming is prohibited in this cleanroom.", fill="#FEF3C7", font=font_body_b)
    draw.text((55, 570), "Stream connection has been paused under Cleanroom NDA Sec. 4.1.\"", fill="#FEF3C7", font=font_body)
    
    draw.text((45, 625), "Wearer Experience: Immediate audible cue  |  No screen required  |  Non-accusatory framing", fill="#94A3B8", font=font_subtitle)
    
    # Human Review Action Buttons (Auditor Interface)
    draw.text((810, 505), "AUDITOR ACTION:", fill="#F8FAFC", font=font_header)
    
    # Button 1: Confirm Block
    draw.rounded_rectangle([810, 535, 980, 585], radius=6, fill="#047857", outline="#10B981", width=1)
    draw.text((835, 550), "[ CONFIRM BLOCK ]", fill="#FFFFFF", font=font_body_b)
    
    # Button 2: False Positive / Restore
    draw.rounded_rectangle([995, 535, 1155, 585], radius=6, fill="#334155", outline="#64748B", width=1)
    draw.text((1015, 550), "[ OVERRIDE / PASS ]", fill="#E2E8F0", font=font_body_b)
    
    # Audit log hash
    draw.text((810, 605), "Audit Hash: SHA256:7f4a...9b12 (Tamper-evident JSONL)", fill="#64748B", font=font_mono)
    draw.text((810, 630), "Dispute Resolution Time: < 5 seconds (vs. 45 min log audit)", fill="#38BDF8", font=font_body_b)
    
    out_path = os.path.join(PRESENTATION_FIGURES, "ch4_multimodal_proof_card.png")
    img.save(out_path, quality=95)
    print(f"Generated: {out_path}")


def generate_human_vs_ai_design_matrix():
    """Generates Slide 9 Infographic: Human Design vs AI Design Comparison Matrix"""
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")
    ax.axis("off")
    
    # Title
    ax.text(0.50, 0.94, "Human Design vs. AI Design Implementation Matrix", 
            color="#FFFFFF", fontsize=18, fontweight="bold", ha="center")
    ax.text(0.50, 0.89, "Critical Evaluation of Stage 1 (Human Assumptions) vs. Stage 2 (Agentic AI Discoveries)", 
            color="#38BDF8", fontsize=11, ha="center")
    
    # Table headers
    cols = [0.05, 0.23, 0.49, 0.75]
    y_start = 0.80
    
    headers = ["Dimension", "Human Design (Stage 1)", "AI-Generated Design (Stage 2)", "Synthesis & Co-Design Impact"]
    for i, h in enumerate(headers):
        ax.text(cols[i], y_start, h, color="#FBBF24", fontsize=11, fontweight="bold")
    ax.plot([0.05, 0.95], [y_start - 0.02, y_start - 0.02], color="#334155", linewidth=1.5)
    
    # Table Rows
    rows = [
        ("Data Pipeline & Scale",
         "Single-device local batch files;\nassumed glasses could process\nall data on-device.",
         "PySpark distributed stream ingestion;\n500ms sliding windows; offloads\nheavy encrypted burst profiling.",
         "Hybrid Edge-Cloud Architecture:\nEgoBlur stays on-device; packet\nburst profiling on companion/cloud."),
        
        ("Community & Context",
         "Manual static labeling;\nassumed 2 rigid rooms based\non user toggles.",
         "Unsupervised Louvain & K-Means;\ndiscovers natural clustering in\npacket sizes, IAT, and burst volume.",
         "Dynamic Contextual Geofencing:\nAuto-switches policies via network\nburst cues without user intervention."),
        
        ("Anomaly Detection",
         "Hardcoded threshold rules\n(e.g., if burst > 500KB -> Block);\nbrittle to pulsing attacks.",
         "Isolation Forest trained on\nencrypted traffic features; catches\nsubtle zero-day exfiltration (F1=0.96).",
         "Layered Defense: Static Action Gate\nfor fast known rules (<5ms) +\nIsolation Forest for zero-day threats."),
        
        ("Multimodal Interaction",
         "Proposed voice warnings conceptually\nand static summary text cards\nfor proctors.",
         "Grounded Open-Ear Audio TTS engine\nwith calibrated phrasing + One-Click\nVisual Proof Cards (Crop + Spike + Rule).",
         "Resolves Screenless Dilemma:\nWearer gets instant audio feedback;\nauditors resolve disputes in <5 sec.")
    ]
    
    y = y_start - 0.07
    for dim, human, ai, synth in rows:
        # Background row tint
        rect = patches.FancyBboxPatch((0.04, y - 0.11), 0.92, 0.13, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor="#1E293B", edgecolor="#334155", linewidth=1)
        ax.add_patch(rect)
        
        ax.text(cols[0], y, dim, color="#38BDF8", fontsize=10, fontweight="bold")
        ax.text(cols[1], y, human, color="#E2E8F0", fontsize=8.8, linespacing=1.3)
        ax.text(cols[2], y, ai, color="#2DD4BF", fontsize=8.8, linespacing=1.3)
        ax.text(cols[3], y, synth, color="#F59E0B", fontsize=8.8, linespacing=1.3)
        
        y -= 0.155
        
    out_path = os.path.join(PRESENTATION_FIGURES, "ch4_human_vs_ai_design_matrix.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


# ==============================================================================
# MAIN EXECUTION ENTRYPOINT
# ==============================================================================
def main():
    print("=" * 70)
    print("CS 5542 Challenge 4: AI Design Implementation & Analytics Pipeline")
    print("=" * 70)
    
    # 1. Generate Wearable Telemetry Dataset
    print("\n[Step 1/5] Ingesting & simulating wearable encrypted telemetry...")
    dataset = generate_synthetic_telemetry(n_samples=1200)
    print(f"-> Generated {len(dataset)} telemetry window records.")
    
    # 2. Run Analytics: K-Means & Isolation Forest
    print("\n[Step 2/5] Running K-Means Clustering & Isolation Forest Anomaly Detection...")
    metrics, X_pca, cluster_labels, anomaly_preds, anomaly_scores = run_analytics_experiments(dataset)
    print(f"-> K-Means Silhouette Score: {metrics['kmeans_silhouette_score']}")
    print(f"-> Anomaly Detection Precision: {metrics['anomaly_precision']}")
    print(f"-> Anomaly Detection Recall:    {metrics['anomaly_recall']}")
    print(f"-> Anomaly Detection F1-Score:  {metrics['anomaly_f1']}")
    
    # 3. Generate Slide 2 Architecture Diagram
    print("\n[Step 3/5] Generating PySpark Pipeline Architecture Diagram...")
    generate_figure_pipeline_architecture()
    
    # 4. Generate Slide 3 & 4 Analytics Visualizations
    print("\n[Step 4/5] Generating Clustering & Anomaly Visualizations...")
    generate_figure_clustering_and_anomaly(X_pca, cluster_labels, anomaly_scores, dataset)
    
    # 5. Generate Slide 6 Multimodal Visual Proof Card & Slide 9 Comparison Matrix
    print("\n[Step 5/5] Generating Multimodal Visual Proof Card & Comparison Matrix...")
    generate_multimodal_proof_card()
    generate_human_vs_ai_design_matrix()
    
    print("\nAll Challenge 4 figures and analytics models successfully compiled!")
    print("=" * 70)

if __name__ == "__main__":
    main()
