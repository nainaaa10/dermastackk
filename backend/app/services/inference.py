"""
Dermastack Machine Learning Inference & Pipeline Service.

Coordinates image preprocessing, HybridSkinNet model evaluation, Grad-CAM heatmap
synthesis, uncertainty rejection policies, and database persistence.
"""

from typing import Dict, Any, Optional, Tuple, List
import uuid
from datetime import datetime, timezone
import hashlib
import asyncio
import torch
import torch.nn.functional as F

from ml.model import HybridSkinNet, set_seed
from ml.labels import SKIN_CLASSES, NUM_CLASSES, CONFIDENCE_THRESHOLD, ENTROPY_THRESHOLD
from ml.preprocessing import validate_and_decode_image, prepare_input_tensor
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.database import db_manager
from backend.app.models.responses import AnalysisResponse, ClassPrediction
from backend.app.services.heatmap import heatmap_service


class InferenceService:
    """Manages model lifecycle, execution mode, and inference workflows."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = HybridSkinNet(num_classes=NUM_CLASSES)
        self.model.to(self.device)
        self.model.eval()

        self.weights_loaded: bool = False
        self.load_status_message: str = "Uninitialized"
        self.diagnostic_code: str = "demo_mode_active" if settings.DEMO_MODE else "missing_weights"

        # Initialize weights
        self._initialize_model()

    def _initialize_model(self):
        """Attempts to load pre-trained weights if present."""
        if settings.DEMO_MODE:
            logger.info("Application configured in DEMO_MODE=True. Initializing in Simulated Demo Mode.")
            self.weights_loaded = False
            self.load_status_message = "Demo Mode configured explicitly via environment settings."
            self.diagnostic_code = "demo_mode_active"
            return

        success, code, msg = self.model.load_weights(settings.MODEL_WEIGHTS_PATH, device=self.device)
        self.weights_loaded = success
        self.load_status_message = msg
        self.diagnostic_code = code
        if success:
            logger.info("HybridSkinNet loaded checkpoint successfully: %s", msg)
        else:
            logger.warning("Checkpoint load failed [%s]: %s. Defaulting to Simulated Demo Mode.", code, msg)

    @property
    def inference_mode(self) -> str:
        if self.weights_loaded and not settings.DEMO_MODE:
            return "trained_inference"
        return "demo_simulated"

    def _generate_deterministic_demo_predictions(self, image_bytes: bytes) -> Tuple[List[ClassPrediction], int, float, bool, Optional[str]]:
        """
        Produces realistic, deterministic demo predictions derived from a hash of image bytes.
        Never fabricates clinical accuracy and clearly labels results as simulated.
        """
        hasher = hashlib.sha256(image_bytes)
        digest = hasher.digest()
        seed_val = int.from_bytes(digest[:4], "big")

        top_idx = seed_val % NUM_CLASSES

        raw_scores = []
        for i in range(NUM_CLASSES):
            if i == top_idx:
                raw_scores.append(2.5 + (digest[i % len(digest)] % 10) * 0.1)
            else:
                raw_scores.append(0.5 + (digest[i % len(digest)] % 10) * 0.05)

        exp_scores = [pow(2.71828, s) for s in raw_scores]
        total_exp = sum(exp_scores)
        probs = [round(s / total_exp, 4) for s in exp_scores]

        top_prob = probs[top_idx]
        is_uncertain = top_prob < CONFIDENCE_THRESHOLD
        uncertainty_reason = (
            "Confidence level is below the minimum threshold (50.0%) for reliable differentiation."
            if is_uncertain else None
        )

        predictions: List[ClassPrediction] = []
        for i in range(NUM_CLASSES):
            c_info = SKIN_CLASSES[i]
            predictions.append(ClassPrediction(
                class_id=c_info["id"],
                name=c_info["name"],
                category=c_info["category"],
                score=probs[i],
                description=c_info["description"],
                educational_notes=c_info["educational_notes"]
            ))

        predictions.sort(key=lambda p: p.score, reverse=True)
        return predictions, top_idx, top_prob, is_uncertain, uncertainty_reason

    def _run_trained_inference(
        self,
        tensor: torch.Tensor
    ) -> Tuple[List[ClassPrediction], int, float, bool, Optional[str]]:
        """Executes actual forward pass on loaded trained PyTorch weights."""
        with torch.no_grad():
            logits = self.model(tensor)
            probs_t = F.softmax(logits, dim=1).squeeze(0)

        probs = probs_t.cpu().tolist()
        top_idx = int(torch.argmax(probs_t).item())
        top_prob = round(probs[top_idx], 4)

        # Calculate Shannon entropy (nats)
        entropy = -sum(p * torch.log(torch.tensor(p + 1e-12)).item() for p in probs)

        is_uncertain = False
        uncertainty_reason = None

        if top_prob < CONFIDENCE_THRESHOLD:
            is_uncertain = True
            uncertainty_reason = f"Primary score ({top_prob * 100:.1f}%) is below the minimum confidence threshold ({CONFIDENCE_THRESHOLD * 100:.0f}%)."
        elif entropy > ENTROPY_THRESHOLD:
            is_uncertain = True
            uncertainty_reason = f"Model output entropy ({entropy:.2f}) indicates an ambiguous or dispersed feature representation."

        predictions: List[ClassPrediction] = []
        for i in range(NUM_CLASSES):
            c_info = SKIN_CLASSES[i]
            predictions.append(ClassPrediction(
                class_id=c_info["id"],
                name=c_info["name"],
                category=c_info["category"],
                score=round(probs[i], 4),
                description=c_info["description"],
                educational_notes=c_info["educational_notes"]
            ))

        predictions.sort(key=lambda p: p.score, reverse=True)
        return predictions, top_idx, top_prob, is_uncertain, uncertainty_reason

    async def analyze_image(
        self,
        image_bytes: bytes,
        user_metadata: Optional[Dict[str, Any]] = None,
        consent_to_save: bool = True
    ) -> AnalysisResponse:
        """
        Executes end-to-end processing pipeline on an uploaded image.
        Offloads CPU/GPU model forward passes to threadpool.
        """
        meta = user_metadata or {}
        report_id = f"rpt_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # 1. Safely decode, validate, and orientation-correct image
        original_pil, aligned_pil = validate_and_decode_image(image_bytes)

        # 2. Prepare PyTorch input tensor
        tensor = prepare_input_tensor(aligned_pil, device=self.device)

        # 3. Model forward pass (offloaded to thread to preserve async I/O)
        mode = self.inference_mode
        if mode == "trained_inference":
            predictions, top_idx, top_prob, is_uncertain, uncertainty_reason = await asyncio.to_thread(
                self._run_trained_inference, tensor
            )
        else:
            predictions, top_idx, top_prob, is_uncertain, uncertainty_reason = self._generate_deterministic_demo_predictions(
                image_bytes
            )

        # 4. Generate Grad-CAM or return explicit diagnostic status
        heatmap_uri, grad_status, grad_explanation, grad_details = await asyncio.to_thread(
            heatmap_service.generate_heatmap, self.model, tensor, aligned_pil, top_idx
        )

        top_pred = predictions[0]

        educational_summary = (
            f"Analysis completed under {mode.upper()} mode. "
            f"Visual features aligned most closely with '{top_pred.name}' category. "
            f"{top_pred.educational_notes}"
        )

        disclaimer = (
            "Dermastack is an educational machine learning research tool, NOT a diagnostic medical device. "
            "It cannot and does not diagnose skin conditions or rule out malignancy. "
            "Consult a board-certified dermatologist for any new, changing, symptomatic, or concerning skin lesions."
        )

        # 5. Database Persistence
        is_persisted = False
        persistence_storage = "none"

        if consent_to_save:
            report_doc = {
                "report_id": report_id,
                "created_at": timestamp,
                "inference_mode": mode,
                "model_version": settings.MODEL_VERSION,
                "predicted_label": top_pred.class_id,
                "predicted_name": top_pred.name,
                "confidence_score": top_pred.score,
                "is_uncertain": is_uncertain,
                "uncertainty_reason": uncertainty_reason,
                "predictions": [p.model_dump() for p in predictions],
                "gradcam_heatmap": heatmap_uri,
                "gradcam_status": grad_status,
                "gradcam_explanation": grad_explanation,
                "gradcam_details": grad_details,
                "educational_summary": educational_summary,
                "disclaimer": disclaimer,
                "user_metadata": meta
            }
            is_persisted, persistence_storage = await db_manager.save_report(report_doc)

        return AnalysisResponse(
            report_id=report_id,
            created_at=timestamp,
            inference_mode=mode,
            model_version=settings.MODEL_VERSION,
            predicted_label=top_pred.class_id,
            predicted_name=top_pred.name,
            confidence_score=top_pred.score,
            is_uncertain=is_uncertain,
            uncertainty_reason=uncertainty_reason,
            predictions=predictions,
            gradcam_heatmap=heatmap_uri,
            gradcam_status=grad_status,
            gradcam_explanation=grad_explanation,
            gradcam_details=grad_details,
            educational_summary=educational_summary,
            disclaimer=disclaimer,
            is_persisted=is_persisted,
            persistence_storage=persistence_storage,
            user_metadata=meta
        )


inference_service = InferenceService()
