"""
System Health and Diagnostics Endpoint.
"""

from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.core.database import db_manager
from backend.app.services.inference import inference_service
from backend.app.models.responses import HealthResponse

router = APIRouter(tags=["Health & Status"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Returns application status, database connectivity, inference mode,
    and checkpoint loading status without exposing internal credentials.
    """
    return HealthResponse(
        status="healthy",
        app_version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        demo_mode=settings.DEMO_MODE,
        database_connected=db_manager.is_connected,
        database_type=db_manager.db_type,
        inference_mode=inference_service.inference_mode,
        weights_loaded=inference_service.weights_loaded,
        checkpoint_status=inference_service.diagnostic_code,
        device=inference_service.device
    )
