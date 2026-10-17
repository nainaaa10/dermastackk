"""
Unit Tests for Machine Learning Architecture, Preprocessing, and Explainability.
"""

import pytest
import torch
from PIL import Image
from ml.model import HybridSkinNet
from ml.preprocessing import validate_and_decode_image, prepare_input_tensor, ImageValidationError
from ml.gradcam import GradCAMExplainer
from backend.tests.test_analyze import create_test_image_bytes


def test_hybrid_skin_net_forward():
    model = HybridSkinNet(num_classes=7)
    model.eval()
    x = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (2, 7)


def test_missing_weights_graceful_handling():
    model = HybridSkinNet(num_classes=7)
    success, msg = model.load_weights("ml/weights/non_existent_weights.pt")
    assert success is False
    assert model.is_trained is False
    assert "not found" in msg.lower()


def test_preprocessing_and_alignment():
    img_bytes = create_test_image_bytes(format="JPEG", size=(500, 300))
    orig, aligned = validate_and_decode_image(img_bytes)
    assert aligned.size == (224, 224)
    assert aligned.mode == "RGB"

    tensor = prepare_input_tensor(aligned)
    assert tensor.shape == (1, 3, 224, 224)
    assert tensor.dtype == torch.float32


def test_preprocessing_invalid_dimension():
    # Less than 64x64
    tiny_bytes = create_test_image_bytes(size=(32, 32))
    with pytest.raises(ImageValidationError) as exc_info:
        validate_and_decode_image(tiny_bytes)
    assert "too small" in str(exc_info.value).lower()


def test_gradcam_untrained_fallback():
    model = HybridSkinNet(num_classes=7)
    model.is_trained = False  # Untrained model
    explainer = GradCAMExplainer(model)
    dummy_tensor = torch.randn(1, 3, 224, 224)
    dummy_pil = Image.new("RGB", (224, 224), color=(100, 100, 100))

    heatmap_uri, meta = explainer.generate(dummy_tensor, dummy_pil)
    assert heatmap_uri is None
    assert meta["available"] is False
    assert "no trained model weights" in meta["reason"].lower()
