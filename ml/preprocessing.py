"""
Dermastack Image Preprocessing & Validation Pipeline.

Provides safe decoding, EXIF orientation correction, dimension verification,
standardization, and tensor preparation for the HybridSkinNet model.
"""

from typing import Tuple, Optional
import io
from PIL import Image, ImageOps
import torch
import torchvision.transforms as T

# Standard input dimensions for HybridSkinNet
TARGET_IMAGE_SIZE: Tuple[int, int] = (224, 224)

# File constraints
MAX_IMAGE_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
MIN_IMAGE_DIMENSION: int = 64
MAX_IMAGE_DIMENSION: int = 4096
ALLOWED_IMAGE_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}

# Standard ImageNet normalization coefficients
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]

# Preprocessing transform
_preprocess_transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(TARGET_IMAGE_SIZE),
    T.ToTensor(),
    T.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD)
])

# Inverse normalization transform (for reconstructing visualization if needed)
_inv_normalize = T.Normalize(
    mean=[-m / s for m, s in zip(NORMALIZE_MEAN, NORMALIZE_STD)],
    std=[1.0 / s for s in NORMALIZE_STD]
)


class ImageValidationError(Exception):
    """Raised when an uploaded image fails security, dimension, or format validation."""
    pass


def validate_and_decode_image(image_bytes: bytes) -> Tuple[Image.Image, Image.Image]:
    """
    Safely validate raw uploaded bytes and return the oriented original image
    and an aligned 224x224 RGB image for visual explainability.

    Args:
        image_bytes: Raw bytes from multipart upload.

    Returns:
        Tuple of (oriented_original_pil, aligned_display_pil)

    Raises:
        ImageValidationError: If image is empty, malformed, unsupported, or out of size limits.
    """
    if not image_bytes or len(image_bytes) == 0:
        raise ImageValidationError("Uploaded image file is empty (0 bytes).")

    if len(image_bytes) > MAX_IMAGE_FILE_SIZE_BYTES:
        raise ImageValidationError(
            f"Image file size ({len(image_bytes) / 1024 / 1024:.2f} MB) exceeds maximum allowed {MAX_IMAGE_FILE_SIZE_BYTES / 1024 / 1024:.0f} MB."
        )

    try:
        stream = io.BytesIO(image_bytes)
        img = Image.open(stream)
        img_format = (img.format or "").upper()
        if img_format not in ALLOWED_IMAGE_FORMATS:
            raise ImageValidationError(
                f"Unsupported image format: '{img_format}'. Allowed formats are: {', '.join(sorted(ALLOWED_IMAGE_FORMATS))}."
            )

        # Force image data loading to catch corrupt bytes
        img.load()
    except ImageValidationError:
        raise
    except Exception as e:
        raise ImageValidationError(f"Invalid or corrupted image data: {str(e)}")

    # Check dimensions
    width, height = img.size
    if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) are too small. Minimum required dimension is {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} pixels."
        )
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) exceed maximum allowed {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels."
        )

    # Correct EXIF orientation if present (common in smartphone dermatology photos)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass  # If EXIF reading fails, continue with original

    # Convert to standard RGB (drops alpha channel or palette indices safely)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Create aligned 224x224 display image matching model input field of view
    # Resize shortest edge to 256, center crop to 224x224
    short_edge = min(img.width, img.height)
    scale = 256.0 / short_edge
    new_w = int(round(img.width * scale))
    new_h = int(round(img.height * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

    left = (new_w - TARGET_IMAGE_SIZE[0]) // 2
    top = (new_h - TARGET_IMAGE_SIZE[1]) // 2
    right = left + TARGET_IMAGE_SIZE[0]
    bottom = top + TARGET_IMAGE_SIZE[1]
    aligned_display = resized.crop((left, top, right, bottom))

    return img, aligned_display


def prepare_input_tensor(aligned_image: Image.Image, device: str = "cpu") -> torch.Tensor:
    """
    Transforms an aligned PIL image into a normalized PyTorch tensor.

    Args:
        aligned_image: Aligned PIL RGB image of size (224, 224).
        device: 'cpu' or 'cuda'.

    Returns:
        Tensor of shape (1, 3, 224, 224) ready for model forward pass.
    """
    # Direct transform from 224x224 aligned image to normalized tensor
    tensor = T.functional.to_tensor(aligned_image)
    tensor = T.functional.normalize(tensor, mean=NORMALIZE_MEAN, std=NORMALIZE_STD)
    return tensor.unsqueeze(0).to(device)
