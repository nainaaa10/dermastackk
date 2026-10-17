"""
Grad-CAM Heatmap Service.
Coordinates explainability computation and formats visual overlays for the API.
"""

from typing import Tuple, Optional, Dict, Any
from PIL import Image
import torch

from ml.gradcam import GradCAMExplainer
from backend.app.core.config import settings


class HeatmapService:
    """Service wrapper for generating and formatting model attention heatmaps."""

    @staticmethod
    def generate_heatmap(
        model: torch.nn.Module,
        input_tensor: torch.Tensor,
        aligned_pil: Image.Image,
        target_class_idx: Optional[int] = None
    ) -> Tuple[Optional[str], str, Optional[str], Dict[str, Any]]:
        """
        Computes Grad-CAM overlay and returns (data_uri, status, explanation, details_dict).
        
        Diagnostic statuses:
            - 'generated': Grad-CAM successfully generated from verified trained weights.
            - 'demo_mode_active': System configured in DEMO_MODE; weights omitted by policy.
            - 'missing_weights': Checkpoint file not found on disk at configured path.
            - 'incompatible_checkpoint': Checkpoint invalid, corrupted, or class count mismatched.
            - 'unsupported_gradcam_layer': Target convolutional layer not available on model.
            - 'inference_error': Forward or backward gradient computation failed.
        """
        target_layer_name = "cnn.stage3"
        checkpoint_path = settings.MODEL_WEIGHTS_PATH

        base_details = {
            "checkpoint_path": checkpoint_path,
            "architecture": "HybridSkinNet (Multi-Stage CNN + Vision Transformer)",
            "target_layer": target_layer_name,
            "expected_classes": 7,
            "requirements_to_enable": [
                "1. Train HybridSkinNet on a 7-class dermatological dataset (e.g., ISIC 2018/2019/2020 Dermoscopy).",
                f"2. Save the checkpoint dictionary containing 'state_dict' with output shape (7, 256) to '{checkpoint_path}'.",
                "3. Set DEMO_MODE=false in backend/.env.",
                "4. Restart the backend service to verify and load the checkpoint."
            ]
        }

        # Check explicit Demo Mode configuration
        if settings.DEMO_MODE:
            details = dict(base_details)
            details["diagnostic_code"] = "demo_mode_active"
            details["status_message"] = "Application configured in DEMO_MODE=True. Trained weights omitted by policy."
            return (
                None,
                "demo_mode_active",
                "Grad-CAM visual explanation is disabled in Simulated Demo Mode. "
                "Feature heatmaps require verified trained weights to prevent showing arbitrary activations.",
                details
            )

        is_trained = getattr(model, "is_trained", False)
        if not is_trained:
            code = getattr(model, "checkpoint_status", "missing_weights")
            details = dict(base_details)
            details["diagnostic_code"] = code
            if code == "missing_weights":
                msg = f"Model weights not found at '{checkpoint_path}'. Genuine Grad-CAM requires a trained checkpoint."
            else:
                msg = "Model checkpoint file was rejected as incompatible with HybridSkinNet (class count or architecture mismatch)."
            details["status_message"] = msg
            return (
                None,
                code,
                msg,
                details
            )

        # Trained model: generate Grad-CAM
        explainer = GradCAMExplainer(model)
        data_uri, meta = explainer.generate(input_tensor, aligned_pil, target_class_idx)

        diag_code = meta.get("diagnostic_code", "generated" if data_uri else "inference_error")
        details = dict(base_details)
        details["diagnostic_code"] = diag_code

        if data_uri:
            details["target_class_index"] = meta.get("target_class_index")
            details["blend_alpha"] = meta.get("blend_alpha", 0.5)
            details["dimensions"] = meta.get("dimensions", [224, 224])
            return (
                data_uri,
                "generated",
                meta.get("explanation", "Grad-CAM highlights regions influencing the model's prediction."),
                details
            )
        else:
            reason = meta.get("reason", "Grad-CAM generation failed.")
            details["status_message"] = reason
            return (
                None,
                diag_code,
                reason,
                details
            )


heatmap_service = HeatmapService()
