"""
Analysis Report Retrieval and History Endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Path, Query, status
from backend.app.core.database import db_manager
from backend.app.models.responses import AnalysisResponse, ReportSummaryResponse
from backend.app.core.logging import logger

router = APIRouter(tags=["Reports & History"])


@router.get("/reports", response_model=List[ReportSummaryResponse])
async def list_reports(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of reports to return.")
):
    """
    Returns recent analysis reports sorted newest first.
    Includes persistence status (MongoDB vs local demo memory).
    """
    try:
        reports = await db_manager.list_reports(limit=limit)
        summaries = []
        for r in reports:
            summaries.append(ReportSummaryResponse(
                report_id=r["report_id"],
                created_at=r["created_at"],
                inference_mode=r.get("inference_mode", "unknown"),
                predicted_name=r.get("predicted_name", "Unspecified"),
                confidence_score=r.get("confidence_score", 0.0),
                is_uncertain=r.get("is_uncertain", False),
                has_heatmap=bool(r.get("has_heatmap", False)),
                is_persisted=True
            ))
        return summaries
    except Exception as e:
        logger.error("Failed to list reports: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report history."
        )


@router.get("/reports/{report_id}", response_model=AnalysisResponse)
async def get_report_by_id(
    report_id: str = Path(..., description="Unique alphanumeric report identifier.")
):
    """
    Fetches the full analysis record by its unique ID, including class distribution,
    educational advice, and stored Grad-CAM heatmaps.
    """
    if not report_id or not report_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID format."
        )

    report = await db_manager.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' was not found in persistence records."
        )

    return AnalysisResponse(
        report_id=report["report_id"],
        created_at=report["created_at"],
        inference_mode=report.get("inference_mode", "demo_simulated"),
        model_version=report.get("model_version", "v1.0.0"),
        predicted_label=report.get("predicted_label", "unknown"),
        predicted_name=report.get("predicted_name", "Unknown"),
        confidence_score=report.get("confidence_score", 0.0),
        is_uncertain=report.get("is_uncertain", False),
        uncertainty_reason=report.get("uncertainty_reason"),
        predictions=report.get("predictions", []),
        gradcam_heatmap=report.get("gradcam_heatmap"),
        gradcam_status=report.get("gradcam_status", "unavailable"),
        gradcam_explanation=report.get("gradcam_explanation"),
        educational_summary=report.get("educational_summary", ""),
        disclaimer=report.get("disclaimer", ""),
        is_persisted=True,
        persistence_storage=db_manager.db_type,
        user_metadata=report.get("user_metadata", {})
    )
