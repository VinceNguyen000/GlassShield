"""
GlassShield Privacy Engine (Layer 01 Sensors & Privacy)
Wraps EgoBlur models to perform on-device face and license plate detection,
computes processing latency, and applies configurable privacy masking.
"""

import os
import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import cv2
from PIL import Image
import torch
import torchvision


class PrivacyEngine:
    """On-device privacy filter powered by EgoBlur models."""

    def __init__(
        self,
        face_model_path: str = "models/ego_blur_face_gen1.jit",
        lp_model_path: str = "models/ego_blur_lp_gen1.jit",
        device: Optional[str] = None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.face_model_path = face_model_path
        self.lp_model_path = lp_model_path

        self.face_model: Optional[torch.jit.ScriptModule] = None
        self.lp_model: Optional[torch.jit.ScriptModule] = None

        self._load_models()

    def _load_models(self) -> None:
        if os.path.exists(self.face_model_path):
            try:
                self.face_model = torch.jit.load(self.face_model_path, map_location=self.device)
                self.face_model.eval()
            except Exception as e:
                print(f"[PrivacyEngine] Warning loading face model: {e}")
                self.face_model = None

        if os.path.exists(self.lp_model_path):
            try:
                self.lp_model = torch.jit.load(self.lp_model_path, map_location=self.device)
                self.lp_model.eval()
            except Exception as e:
                print(f"[PrivacyEngine] Warning loading LP model: {e}")
                self.lp_model = None

    def _run_model_inference(
        self,
        model: torch.jit.ScriptModule,
        bgr_image: np.ndarray,
        score_threshold: float,
        nms_iou_threshold: float,
    ) -> List[Dict[str, Any]]:
        """Executes inference on a single image and applies NMS."""
        h, w = bgr_image.shape[:2]
        # Transpose HWC -> CHW
        transposed = np.transpose(bgr_image, (2, 0, 1))
        tensor = torch.from_numpy(transposed).to(self.device)

        with torch.no_grad():
            output = model(tensor)

        boxes, labels, scores, dims = output

        # Apply NMS
        nms_indices = torchvision.ops.nms(boxes, scores, nms_iou_threshold)
        boxes = boxes[nms_indices].cpu().numpy()
        scores = scores[nms_indices].cpu().numpy()

        results = []
        for box, score in zip(boxes, scores):
            score_val = float(score)
            if score_val >= score_threshold:
                x1, y1, x2, y2 = [float(v) for v in box]
                # Clamp coordinates to image boundaries
                x1 = max(0.0, min(float(w), x1))
                y1 = max(0.0, min(float(h), y1))
                x2 = max(0.0, min(float(w), x2))
                y2 = max(0.0, min(float(h), y2))
                area_pct = round(((x2 - x1) * (y2 - y1)) / (w * h) * 100.0, 2)
                results.append({
                    "box": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "confidence": round(score_val, 4),
                    "area_pct": area_pct,
                })
        return results

    def process_frame(
        self,
        image_input: Any,  # np.ndarray (BGR or RGB) or PIL.Image
        detect_faces: bool = True,
        detect_plates: bool = True,
        score_threshold: float = 0.50,
        nms_iou_threshold: float = 0.50,
        blur_style: str = "gaussian_blur",  # "gaussian_blur" | "solid_mask" | "pixelate"
        blur_intensity: int = 51,
        scale_box_factor: float = 1.15,
        manual_boxes: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end detection, privacy masking, and telemetry computation.
        """
        # Convert input to numpy BGR image for processing
        if isinstance(image_input, Image.Image):
            rgb_np = np.array(image_input.convert("RGB"))
            bgr_image = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 2:
                bgr_image = cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
            elif image_input.shape[2] == 4:
                bgr_image = cv2.cvtColor(image_input, cv2.COLOR_RGBA2BGR)
            else:
                bgr_image = image_input.copy()
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        h, w = bgr_image.shape[:2]
        start_time = time.perf_counter()

        detected_entities: List[Dict[str, Any]] = []
        entity_id = 1

        # 1. Face detection
        if detect_faces and self.face_model is not None:
            face_results = self._run_model_inference(
                self.face_model, bgr_image, score_threshold, nms_iou_threshold
            )
            for item in face_results:
                detected_entities.append({
                    "entity_id": entity_id,
                    "class_name": "face",
                    "confidence": item["confidence"],
                    "box": item["box"],
                    "area_pct": item["area_pct"],
                    "detection_source": "EgoBlur-Gen1-Face",
                })
                entity_id += 1

        # 2. License plate detection
        if detect_plates and self.lp_model is not None:
            lp_results = self._run_model_inference(
                self.lp_model, bgr_image, score_threshold, nms_iou_threshold
            )
            for item in lp_results:
                detected_entities.append({
                    "entity_id": entity_id,
                    "class_name": "license_plate",
                    "confidence": item["confidence"],
                    "box": item["box"],
                    "area_pct": item["area_pct"],
                    "detection_source": "EgoBlur-Gen1-LP",
                })
                entity_id += 1

        # 3. Incorporate human manual bounding boxes (if any)
        if manual_boxes:
            for m_box in manual_boxes:
                x1, y1, x2, y2 = m_box
                area_pct = round(((x2 - x1) * (y2 - y1)) / (w * h) * 100.0, 2)
                detected_entities.append({
                    "entity_id": entity_id,
                    "class_name": "face (manual)",
                    "confidence": 1.0,
                    "box": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "area_pct": area_pct,
                    "detection_source": "Human-Refinement",
                })
                entity_id += 1

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # 4. Render overlay visual evidence (bounding boxes on original)
        overlay_bgr = bgr_image.copy()
        for ent in detected_entities:
            x1, y1, x2, y2 = [int(v) for v in ent["box"]]
            color = (0, 165, 255) if "face" in ent["class_name"] else (255, 100, 0)
            cv2.rectangle(overlay_bgr, (x1, y1), (x2, y2), color, 3)
            label = f"{ent['class_name']}: {ent['confidence']:.2f}"
            cv2.putText(
                overlay_bgr,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        # 5. Render privacy-masked image
        anonymized_bgr = bgr_image.copy()
        for ent in detected_entities:
            x1, y1, x2, y2 = [int(v) for v in ent["box"]]

            # Apply scale factor to cover margin
            if scale_box_factor > 1.0:
                box_w = x2 - x1
                box_h = y2 - y1
                pad_w = int(box_w * (scale_box_factor - 1.0) / 2)
                pad_h = int(box_h * (scale_box_factor - 1.0) / 2)
                x1 = max(0, x1 - pad_w)
                y1 = max(0, y1 - pad_h)
                x2 = min(w, x2 + pad_w)
                y2 = min(h, y2 + pad_h)

            roi = anonymized_bgr[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            if blur_style == "gaussian_blur":
                ksize = max(3, blur_intensity if blur_intensity % 2 != 0 else blur_intensity + 1)
                blurred_roi = cv2.GaussianBlur(roi, (ksize, ksize), 0)
                anonymized_bgr[y1:y2, x1:x2] = blurred_roi
            elif blur_style == "pixelate":
                pixel_size = max(4, int(min(roi.shape[:2]) / 8))
                small = cv2.resize(roi, (pixel_size, pixel_size), interpolation=cv2.INTER_LINEAR)
                pixelated = cv2.resize(small, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_NEAREST)
                anonymized_bgr[y1:y2, x1:x2] = pixelated
            elif blur_style == "solid_mask":
                # Dark privacy mask with subtle border
                cv2.rectangle(anonymized_bgr, (x1, y1), (x2, y2), (20, 20, 20), -1)
                cv2.rectangle(anonymized_bgr, (x1, y1), (x2, y2), (0, 255, 255), 1)

        # Convert outputs back to RGB for Streamlit/PIL
        original_rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        overlay_rgb = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)
        anonymized_rgb = cv2.cvtColor(anonymized_bgr, cv2.COLOR_BGR2RGB)

        faces_count = sum(1 for e in detected_entities if "face" in e["class_name"])
        plates_count = sum(1 for e in detected_entities if "license_plate" in e["class_name"])

        return {
            "detected_entities": detected_entities,
            "faces_detected": faces_count,
            "plates_detected": plates_count,
            "pii_masked": len(detected_entities) > 0,
            "filter_latency_ms": latency_ms,
            "device": self.device,
            "original_image": original_rgb,
            "overlay_image": overlay_rgb,
            "anonymized_image": anonymized_rgb,
            "image_dimensions": {"width": w, "height": h},
        }
