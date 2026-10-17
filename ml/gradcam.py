"""
Dermastack Grad-CAM Visual Explainability Module.

Generates gradient-weighted class activation mappings (Grad-CAM) to visualize
the spatial regions in a dermatological image that most strongly influence
the hybrid model's classification score.

DISCLAIMER:
Grad-CAM highlights receptive fields that contributed to model logits. It does NOT
verify the presence or absence of skin pathology, nor does it replace professional
clinical dermoscopy examination.
"""

from typing import Tuple, Optional, Dict, Any
import io
import base64
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F


def _apply_colormap_jet(heatmap: np.ndarray) -> np.ndarray:
    """
    Applies a standard Jet colormap to a normalized (0 to 1) 2D float array.
    Returns an RGB image array with shape (H, W, 3) in [0, 255] uint8.
    """
    heatmap = np.clip(heatmap, 0.0, 1.0)
    
    # 4-stage color progression: Blue -> Cyan -> Yellow -> Red
    r = np.clip(1.5 - np.abs(4.0 * heatmap - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * heatmap - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * heatmap - 1.0), 0.0, 1.0)
    
    rgb = np.stack([r, g, b], axis=-1)
    return (rgb * 255.0).astype(np.uint8)


class GradCAMExplainer:
    """
    Hook-based Grad-CAM generator for HybridSkinNet.
    Extracts activations and gradients from the final CNN residual block.
    """

    def __init__(self, model: torch.nn.Module, target_layer: Optional[torch.nn.Module] = None):
        self.model = model
        self.target_layer = target_layer if target_layer is not None else getattr(model, "target_conv_layer", None)
        self.gradients: Optional[torch.Tensor] = None
        self.activations: Optional[torch.Tensor] = None
        self._hook_handles = []

    def _register_hooks(self):
        if self.target_layer is None:
            return

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self._hook_handles.append(self.target_layer.register_forward_hook(forward_hook))
        self._hook_handles.append(self.target_layer.register_full_backward_hook(backward_hook))

    def _remove_hooks(self):
        for handle in self._hook_handles:
            try:
                handle.remove()
            except Exception:
                pass
        self._hook_handles.clear()

    def generate(
        self,
        input_tensor: torch.Tensor,
        aligned_pil: Image.Image,
        target_class_idx: Optional[int] = None,
        alpha: float = 0.5
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Computes Grad-CAM heatmap, overlays it on the aligned image, and returns a base64 PNG data URI.

        Returns:
            Tuple of (base64_data_uri or None, metadata_dict with diagnostic_code)
        """
        if self.target_layer is None:
            return None, {
                "available": False,
                "diagnostic_code": "unsupported_gradcam_layer",
                "reason": "Target convolutional layer not configured or absent on model architecture."
            }

        is_trained = getattr(self.model, "is_trained", False)
        if not is_trained:
            checkpoint_status = getattr(self.model, "checkpoint_status", "missing_weights")
            return None, {
                "available": False,
                "diagnostic_code": checkpoint_status,
                "reason": (
                    "Grad-CAM explanation is unavailable because no trained model weights are loaded. "
                    "Untrained feature activations are random and visually misleading."
                )
            }

        self._register_hooks()
        self.model.eval()

        try:
            with torch.enable_grad():
                input_tensor = input_tensor.clone().requires_grad_(True)
                logits = self.model(input_tensor)

                if target_class_idx is None:
                    target_class_idx = int(torch.argmax(logits, dim=1).item())

                score = logits[0, target_class_idx]
                self.model.zero_grad()
                score.backward(retain_graph=False)

            if self.activations is None or self.gradients is None:
                return None, {
                    "available": False,
                    "diagnostic_code": "inference_error",
                    "reason": "Could not capture gradients or activations during backward pass on target layer."
                }

            # Global average pooling of gradients: weights alpha_k
            weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
            cam = torch.sum(weights * self.activations, dim=1, keepdim=True)
            cam = F.relu(cam)

            # Interpolate to input image size (224, 224)
            cam = F.interpolate(cam, size=(aligned_pil.height, aligned_pil.width), mode="bilinear", align_corners=False)
            cam_np = cam.squeeze().cpu().numpy()

            cam_min, cam_max = cam_np.min(), cam_np.max()
            if cam_max - cam_min > 1e-8:
                cam_norm = (cam_np - cam_min) / (cam_max - cam_min)
            else:
                cam_norm = np.zeros_like(cam_np)

            heatmap_rgb = _apply_colormap_jet(cam_norm)
            heatmap_pil = Image.fromarray(heatmap_rgb, mode="RGB")

            aligned_rgb = aligned_pil.convert("RGB")
            blended_pil = Image.blend(aligned_rgb, heatmap_pil, alpha=alpha)

            buffer = io.BytesIO()
            blended_pil.save(buffer, format="PNG")
            base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            data_uri = f"data:image/png;base64,{base64_data}"

            return data_uri, {
                "available": True,
                "diagnostic_code": "generated",
                "target_class_index": target_class_idx,
                "blend_alpha": alpha,
                "dimensions": [aligned_pil.width, aligned_pil.height],
                "explanation": "Colored heatmap highlights image regions that contributed most positively to the model's prediction score. Warmer regions (red/yellow) indicate higher influence."
            }

        except Exception as e:
            return None, {
                "available": False,
                "diagnostic_code": "inference_error",
                "reason": f"Grad-CAM generation encountered an unexpected error: {str(e)}"
            }
        finally:
            self._remove_hooks()
            self.activations = None
            self.gradients = None
