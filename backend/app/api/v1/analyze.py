"""
Skin Image Analysis Endpoint.
Receives user images, validates inputs, coordinates ML inference, and formats responses.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from ml.preprocessing import ImageValidationError, MAX_IMAGE_FILE_SIZE_BYTES
from backend.app.services.inference import inference_service
from backend.app.models.responses import AnalysisResponse
from backend.app.core.logging import logger

router = APIRouter(tags=["Skin Analysis"])


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_skin_image(
    image: UploadFile = File(..., description="Dermatological image file (JPEG, PNG, WEBP)."),
    age_range: Optional[str] = Form(None, description="Optional age bracket (e.g. '18-29', '30-45', '46-60', '60+')."),
    skin_type: Optional[str] = Form(None, description="Optional self-identified Fitzpatrick skin type or description."),
    concerns: Optional[str] = Form(None, description="Optional reported symptoms or visual concerns."),
    consent_to_save: bool = Form(True, description="Explicit user consent to persist report in database.")
):
    """
    Submits a skin image for experimental machine learning feature analysis.
    
    Accepts:
        - Image file (multipart/form-data)
        - Optional context parameters (age_range, skin_type, concerns)
        - Optional consent flag to control report persistence
        
    Returns:
        Structured AnalysisResponse with class scores, educational guidance, and explainability heatmaps.
    """
    # 1. Validate content type header
    content_type = (image.content_type or "").lower()
    allowed_content_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    if content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file MIME type: '{content_type}'. Must be JPEG, PNG, or WEBP."
        )

    # 2. Read image bytes and enforce file size
    try:
        image_bytes = await image.read()
    except Exception as e:
        logger.error("Failed to read uploaded image stream: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded image data."
        )

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if len(image_bytes) > MAX_IMAGE_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds maximum allowable limit of {MAX_IMAGE_FILE_SIZE_BYTES / 1024 / 1024:.0f} MB."
        )

    # 3. Execute inference pipeline
    metadata = {
        "filename": image.filename,
        "age_range": age_range,
        "skin_type": skin_type,
        "reported_concerns": concerns
    }

    try:
        response = await inference_service.analyze_image(
            image_bytes=image_bytes,
            user_metadata=metadata,
            consent_to_save=consent_to_save
        )
        return response
    except ImageValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception("Unexpected error during image analysis: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred while processing the image: {str(e)}"
        )
