"""
Cosmetic Ingredient Checker Endpoint.
Evaluates formulations against dermatological evidence and reports potential cautions.
"""

from fastapi import APIRouter, HTTPException, status
from backend.app.models.requests import IngredientCheckRequest, CustomIngredientRequest
from backend.app.models.responses import IngredientCheckResponse
from backend.app.services.ingredients import ingredient_service
from backend.app.core.logging import logger

router = APIRouter(tags=["Ingredient Checker"])


@router.post("/ingredients/check", response_model=IngredientCheckResponse, status_code=status.HTTP_200_OK)
async def check_ingredients(payload: IngredientCheckRequest):
    """
    Analyzes a raw cosmetic ingredient deck against literature-backed skin science data.
    
    Identifies:
        - Documented cosmetic functions (humectant, antioxidant, exfoliant, etc.)
        - Comedogenic & irritancy ratings where validated
        - Ingredient evidence confidence (High, Moderate, Limited, Unknown)
        - Potential conflicts with user-provided skin concerns or known allergies
    """
    if not payload.ingredient_text or not payload.ingredient_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingredient text cannot be empty."
        )

    try:
        result = await ingredient_service.check_formula(
            ingredient_text=payload.ingredient_text,
            skin_concerns=payload.skin_concerns,
            known_sensitivities=payload.known_sensitivities
        )
        return result
    except Exception as e:
        logger.exception("Error checking ingredients: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while evaluating the ingredient formulation: {str(e)}"
        )


@router.post("/ingredients/custom", status_code=status.HTTP_201_CREATED)
async def extend_ingredient_catalog(payload: CustomIngredientRequest):
    """
    Extends the local database with a new verified cosmetic ingredient.
    """
    import re
    from backend.app.core.database import db_manager
    key = re.sub(r"[^a-zA-Z0-9]+", "_", payload.name.lower()).strip("_")
    item = {
        "key": key,
        "name": payload.name,
        "synonyms": payload.synonyms,
        "functions": payload.functions,
        "comedogenic_rating": payload.comedogenic_rating,
        "irritancy_rating": payload.irritancy_rating,
        "evidence_level": payload.evidence_level,
        "safety_profile": payload.safety_profile,
        "cautions": payload.cautions,
        "contraindications": payload.contraindications,
        "sources": payload.sources
    }
    db_manager.seed_ingredients([item])
    return {
        "success": True,
        "message": f"Successfully registered '{payload.name}' in local database.",
        "key": key
    }

