"""
MongoDB Document Models and Serialization helpers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def create_report_document(
    report_id: str,
    inference_mode: str,
    model_version: str,
    predicted_label: str,
    predicted_name: str,
    confidence_score: float,
    is_uncertain: bool,
    uncertainty_reason: Optional[str],
    predictions: List[Dict[str, Any]],
    gradcam_heatmap: Optional[str],
    gradcam_status: str,
    educational_summary: str,
    disclaimer: str,
    user_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Prepares a standardized dictionary document for persistence."""
    return {
        "report_id": report_id,
        "created_at": datetime.utcnow().isoformat(),
        "inference_mode": inference_mode,
        "model_version": model_version,
        "predicted_label": predicted_label,
        "predicted_name": predicted_name,
        "confidence_score": confidence_score,
        "is_uncertain": is_uncertain,
        "uncertainty_reason": uncertainty_reason,
        "predictions": predictions,
        "gradcam_heatmap": gradcam_heatmap,
        "gradcam_status": gradcam_status,
        "educational_summary": educational_summary,
        "disclaimer": disclaimer,
        "user_metadata": user_metadata
    }
