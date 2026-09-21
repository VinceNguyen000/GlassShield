"""
GlassShield Sample Data Loader
Generates and caches representative egocentric test scenarios for testing and demonstration.
"""

import os
from typing import Dict, Any, List
import numpy as np
import cv2
from PIL import Image


class SampleDataLoader:
    """Manages sample egocentric scenarios for offline benchmarks and interactive UI testing."""

    SAMPLE_DIR = os.path.join("data", "sitara_samples")

    @classmethod
    def ensure_samples(cls) -> Dict[str, str]:
        """Creates sample scenario images if not present, and returns scenario name -> path map."""
        os.makedirs(cls.SAMPLE_DIR, exist_ok=True)

        scenarios = {
            "Bystander Portrait (SITARA Real Sample)": os.path.join(cls.SAMPLE_DIR, "bystander_portrait.jpg"),
            "Vehicle License Plate (Urban Traffic)": os.path.join(cls.SAMPLE_DIR, "vehicle_plate.jpg"),
            "Crowded Pedestrian Street (Multi-PII)": os.path.join(cls.SAMPLE_DIR, "crowded_street.jpg"),
            "Clean Meeting Room (True Negative / No PII)": os.path.join(cls.SAMPLE_DIR, "clean_room.jpg"),
            "Low-Light Obscured Bystander (Failure Case)": os.path.join(cls.SAMPLE_DIR, "low_light_edge.jpg"),
            "Textured Wall Art (False Positive Audit)": os.path.join(cls.SAMPLE_DIR, "textured_wall_art.jpg"),
        }

        # 1. Bystander Portrait: use test_output.jpg if available
        if not os.path.exists(scenarios["Bystander Portrait (SITARA Real Sample)"]):
            if os.path.exists("test_output.jpg"):
                img = cv2.imread("test_output.jpg")
                cv2.imwrite(scenarios["Bystander Portrait (SITARA Real Sample)"], img)
            else:
                cls._create_synthetic_face(scenarios["Bystander Portrait (SITARA Real Sample)"])

        # 2. Vehicle License Plate
        if not os.path.exists(scenarios["Vehicle License Plate (Urban Traffic)"]):
            cls._create_synthetic_vehicle(scenarios["Vehicle License Plate (Urban Traffic)"])

        # 3. Crowded Pedestrian Street
        if not os.path.exists(scenarios["Crowded Pedestrian Street (Multi-PII)"]):
            cls._create_synthetic_crowd(scenarios["Crowded Pedestrian Street (Multi-PII)"])

        # 4. Clean Meeting Room
        if not os.path.exists(scenarios["Clean Meeting Room (True Negative / No PII)"]):
            cls._create_synthetic_clean_room(scenarios["Clean Meeting Room (True Negative / No PII)"])

        # 5. Low-Light Edge Case
        if not os.path.exists(scenarios["Low-Light Obscured Bystander (Failure Case)"]):
            cls._create_synthetic_low_light(scenarios["Low-Light Obscured Bystander (Failure Case)"])

        # 6. Textured Wall Art
        if not os.path.exists(scenarios["Textured Wall Art (False Positive Audit)"]):
            cls._create_synthetic_texture(scenarios["Textured Wall Art (False Positive Audit)"])

        return scenarios

    @staticmethod
    def _create_synthetic_face(path: str) -> None:
        """Creates a realistic synthetic head-and-shoulders frame."""
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 230
        # Background gradient
        for y in range(720):
            img[y, :, :] = np.clip(img[y, :, :].astype(int) - int(y * 0.1), 0, 255).astype(np.uint8)
        # Shoulders
        cv2.ellipse(img, (640, 700), (320, 240), 0, 0, 360, (70, 70, 80), -1)
        # Neck
        cv2.rectangle(img, (580, 420), (700, 520), (180, 150, 130), -1)
        # Head / Face
        cv2.ellipse(img, (640, 320), (130, 180), 0, 0, 360, (200, 170, 150), -1)
        # Hair
        cv2.ellipse(img, (640, 240), (140, 110), 0, 180, 360, (40, 30, 25), -1)
        # Eyes
        cv2.ellipse(img, (590, 300), (22, 12), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(img, (690, 300), (22, 12), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(img, (590, 300), 8, (60, 40, 20), -1)
        cv2.circle(img, (690, 300), 8, (60, 40, 20), -1)
        # Nose & Mouth
        cv2.line(img, (640, 310), (640, 350), (150, 120, 100), 3)
        cv2.line(img, (615, 385), (665, 385), (140, 70, 80), 4)
        cv2.imwrite(path, img)

    @staticmethod
    def _create_synthetic_vehicle(path: str) -> None:
        """Creates a vehicle rear scene with a license plate."""
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 180
        # Road
        cv2.rectangle(img, (0, 450), (1280, 720), (60, 60, 60), -1)
        cv2.line(img, (640, 450), (640, 720), (240, 240, 240), 6)
        # Vehicle body
        cv2.rectangle(img, (380, 280), (900, 580), (120, 30, 30), -1)
        cv2.rectangle(img, (440, 160), (840, 280), (100, 25, 25), -1)
        # Rear window
        cv2.rectangle(img, (460, 180), (820, 270), (40, 50, 60), -1)
        # Tail lights
        cv2.rectangle(img, (400, 360), (480, 410), (0, 0, 220), -1)
        cv2.rectangle(img, (800, 360), (880, 410), (0, 0, 220), -1)
        # License plate
        cv2.rectangle(img, (570, 460), (710, 510), (240, 240, 240), -1)
        cv2.rectangle(img, (570, 460), (710, 510), (10, 10, 10), 2)
        cv2.putText(img, "7XYZ890", (580, 495), cv2.FONT_HERSHEY_DUPLEX, 0.9, (10, 10, 10), 2)
        cv2.imwrite(path, img)

    @staticmethod
    def _create_synthetic_crowd(path: str) -> None:
        """Creates a crowd scene with multiple bystanders at various positions."""
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 210
        # Pavement
        cv2.rectangle(img, (0, 500), (1280, 720), (100, 100, 105), -1)
        # Person 1 (Center-Left)
        cv2.ellipse(img, (380, 400), (55, 75), 0, 0, 360, (190, 160, 140), -1)
        cv2.ellipse(img, (380, 350), (60, 45), 0, 180, 360, (30, 20, 20), -1)
        cv2.rectangle(img, (310, 475), (450, 700), (40, 80, 120), -1)

        # Person 2 (Center-Right)
        cv2.ellipse(img, (850, 380), (65, 85), 0, 0, 360, (210, 175, 155), -1)
        cv2.ellipse(img, (850, 320), (70, 55), 0, 180, 360, (70, 50, 30), -1)
        cv2.rectangle(img, (760, 465), (940, 700), (80, 50, 80), -1)

        # Person 3 (Distant Center)
        cv2.ellipse(img, (600, 340), (28, 38), 0, 0, 360, (195, 165, 145), -1)
        cv2.rectangle(img, (565, 378), (635, 520), (50, 110, 60), -1)
        cv2.imwrite(path, img)

    @staticmethod
    def _create_synthetic_clean_room(path: str) -> None:
        """Creates a clean indoor room / plant environment with zero human PII or plate artifacts."""
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 235
        # Soft wall gradient
        for y in range(450):
            img[y, :, :] = np.clip(img[y, :, :].astype(int) - int(y * 0.08), 0, 255).astype(np.uint8)
        # Wooden floor
        cv2.rectangle(img, (0, 450), (1280, 720), (140, 100, 70), -1)
        # Sofa / couch
        cv2.rectangle(img, (250, 420), (1030, 600), (180, 70, 70), -1)
        cv2.ellipse(img, (640, 420), (390, 40), 0, 0, 180, (160, 60, 60), -1)
        # Cushions
        cv2.rectangle(img, (320, 440), (500, 560), (220, 180, 100), -1)
        cv2.rectangle(img, (780, 440), (960, 560), (220, 180, 100), -1)
        # Large indoor potted plants
        cv2.rectangle(img, (80, 480), (180, 640), (120, 80, 50), -1)
        cv2.circle(img, (130, 420), 70, (40, 120, 40), -1)
        cv2.circle(img, (90, 380), 55, (30, 140, 30), -1)
        cv2.circle(img, (170, 390), 60, (50, 150, 50), -1)

        cv2.rectangle(img, (1100, 480), (1200, 640), (120, 80, 50), -1)
        cv2.circle(img, (1150, 420), 70, (40, 120, 40), -1)
        cv2.circle(img, (1110, 380), 55, (30, 140, 30), -1)
        cv2.circle(img, (1190, 390), 60, (50, 150, 50), -1)
        cv2.imwrite(path, img)

    @staticmethod
    def _create_synthetic_low_light(path: str) -> None:
        """Creates a dim, low-contrast night scene with an obscured distant face."""
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 25
        # Street lamp glow in corner
        cv2.circle(img, (1100, 150), 120, (50, 60, 70), -1)
        # Obscured distant silhouette
        cv2.ellipse(img, (450, 380), (32, 42), 0, 0, 360, (55, 48, 42), -1)
        cv2.rectangle(img, (400, 422), (500, 650), (35, 35, 40), -1)
        cv2.imwrite(path, img)

    @staticmethod
    def _create_synthetic_texture(path: str) -> None:
        """Creates an artistic textured wall with geometric patterns for FPR testing."""
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 215
        # Abstract circles and shapes that may mimic facial proportions to test detector specificity
        for i in range(5):
            cx = 250 + i * 180
            cy = 360
            cv2.circle(img, (cx, cy), 65, (160 + i * 10, 130, 120), -1)
            cv2.circle(img, (cx - 20, cy - 15), 10, (50, 50, 50), -1)
            cv2.circle(img, (cx + 20, cy - 15), 10, (50, 50, 50), -1)
            cv2.arcLength(np.array([[cx - 20, cy + 25], [cx, cy + 35], [cx + 20, cy + 25]]), False)
            cv2.ellipse(img, (cx, cy + 25), (20, 8), 0, 0, 180, (70, 70, 70), 2)
        cv2.putText(img, "MODERN ART GALLERY EXHIBIT", (340, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (80, 80, 80), 2)
        cv2.imwrite(path, img)
