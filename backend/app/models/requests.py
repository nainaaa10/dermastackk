"""
Request Schemas for Dermastack Endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class IngredientCheckRequest(BaseModel):
    """Request payload for cosmetic ingredient verification."""
    ingredient_text: str = Field(
        ...,
        min_length=2,
        max_length=15000,
        description="Raw or comma-separated cosmetic ingredient list copied from product packaging."
    )
    skin_concerns: Optional[List[str]] = Field(
        default=None,
        description="Optional self-reported skin concerns (e.g., acne, rosacea, sensitive, barrier_compromise)."
    )
    known_sensitivities: Optional[List[str]] = Field(
        default=None,
        description="Optional list of user-known sensitivities or allergens (e.g., fragrance, linalool, sulfates)."
    )


class ReportQueryRequest(BaseModel):
    """Optional query parameters for listing stored reports."""
    limit: int = Field(default=20, ge=1, le=100)


class CustomIngredientRequest(BaseModel):
    """Payload to extend the local database with verified ingredients."""
    name: str = Field(..., min_length=2, max_length=150)
    synonyms: List[str] = Field(default_factory=list)
    functions: List[str] = Field(default_factory=list)
    comedogenic_rating: Optional[int] = Field(None, ge=0, le=5)
    irritancy_rating: Optional[int] = Field(None, ge=0, le=5)
    evidence_level: str = Field("Moderate", description="'High', 'Moderate', or 'Limited'")
    safety_profile: str = Field(..., min_length=10)
    cautions: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)

