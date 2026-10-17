"""
Response Schemas for Dermastack Endpoints.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health and runtime status response."""
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    app_version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    environment: str = Field(..., json_schema_extra={"example": "development"})
    demo_mode: bool = Field(..., json_schema_extra={"example": True})
    database_connected: bool = Field(..., json_schema_extra={"example": False})
    database_type: str = Field(..., json_schema_extra={"example": "in_memory_demo"})
    inference_mode: str = Field(..., json_schema_extra={"example": "demo_mode"})
    weights_loaded: bool = Field(..., json_schema_extra={"example": False})
    checkpoint_status: str = Field("missing_weights", json_schema_extra={"example": "missing_weights"})
    device: str = Field(..., json_schema_extra={"example": "cpu"})


class ClassPrediction(BaseModel):
    """Detailed score and educational description for a candidate skin condition."""
    class_id: str
    name: str
    category: str
    score: float = Field(..., ge=0.0, le=1.0)
    description: str
    educational_notes: str


class AnalysisResponse(BaseModel):
    """Complete response payload for an image analysis report."""
    report_id: str
    created_at: str
    inference_mode: str = Field(..., description="'demo_simulated' or 'trained_inference'")
    model_version: str
    predicted_label: str
    predicted_name: str
    confidence_score: float
    is_uncertain: bool
    uncertainty_reason: Optional[str] = None
    predictions: List[ClassPrediction]
    gradcam_heatmap: Optional[str] = Field(None, description="Base64 PNG data URI or None")
    gradcam_status: str = Field(
        ...,
        description="'generated', 'demo_mode_active', 'missing_weights', 'incompatible_checkpoint', 'unsupported_gradcam_layer', or 'inference_error'"
    )
    gradcam_explanation: Optional[str] = None
    gradcam_details: Optional[Dict[str, Any]] = None
    educational_summary: str
    disclaimer: str
    is_persisted: bool
    persistence_storage: str
    user_metadata: Dict[str, Any] = Field(default_factory=dict)


class IngredientSourceItem(BaseModel):
    """Structured literature citation or reference URL."""
    title: str
    citation_or_url: str
    accessed_date: str = "October 2026"


class IngredientItemResponse(BaseModel):
    """Cosmetic and dermatological metadata for a single parsed ingredient."""
    query_name: str
    matched_name: str
    is_known: bool
    match_type: str = Field(
        "unknown_ingredient",
        description="'exact_match', 'alias_match', 'incomplete_evidence', or 'unknown_ingredient'"
    )
    matched_alias: Optional[str] = None
    functions: List[str] = Field(default_factory=list)
    comedogenic_rating: Optional[int] = Field(None, ge=0, le=5)
    irritancy_rating: Optional[int] = Field(None, ge=0, le=5)
    evidence_level: str = Field("Unknown", description="'High', 'Moderate', 'Limited', or 'Unknown'")
    safety_profile: str
    cautions: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)
    sources: List[Union[IngredientSourceItem, str]] = Field(default_factory=list)


class IngredientCheckResponse(BaseModel):
    """Analysis results for a submitted skincare ingredient formulation."""
    total_parsed: int
    total_identified: int
    total_unknown: int
    ingredients: List[IngredientItemResponse]
    unknown_ingredients: List[str]
    potential_flags: List[str]
    educational_overview: str
    disclaimer: str
    extension_guidance: Optional[str] = None


class ReportSummaryResponse(BaseModel):
    """Summary record for displaying analysis history."""
    report_id: str
    created_at: str
    inference_mode: str
    predicted_name: str
    confidence_score: float
    is_uncertain: bool
    has_heatmap: bool = False
    is_persisted: bool = True
