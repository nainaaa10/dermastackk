"""
Dermastack Machine Learning Label Definitions and Metadata.

This module defines the skin concern / lesion classes supported by the
experimental Hybrid CNN + Vision Transformer model.

DISCLAIMER:
Dermastack is strictly an educational and experimental platform. These labels
and their descriptions are provided for machine learning classification research
and do NOT constitute clinical diagnostic findings or replace a medical professional.
"""

from typing import Dict, Any

# Minimum softmax probability score required to assign a confident label.
# Predictions below this threshold are marked as 'inconclusive / uncertain'.
CONFIDENCE_THRESHOLD: float = 0.50

# Maximum Shannon entropy threshold (in nats) above which prediction is considered dispersed / uncertain.
ENTROPY_THRESHOLD: float = 1.35

SKIN_CLASSES: Dict[int, Dict[str, Any]] = {
    0: {
        "id": "benign_keratosis_like_lesions",
        "name": "Benign Keratosis-like Lesions",
        "description": "Common, non-cancerous skin growths such as seborrheic keratoses or solar lentigines (sun spots), often warty or flat-pigmented.",
        "category": "Keratinocyte / Pigmentary",
        "educational_notes": "Seborrheic keratoses are very common as skin ages and are benign. However, sudden changes in texture or rapid growth should always be evaluated by a dermatologist."
    },
    1: {
        "id": "melanocytic_nevi",
        "name": "Melanocytic Nevi (Common Moles)",
        "description": "Benign proliferations of melanocytes presenting as evenly pigmented, circumscribed macules, papules, or plaques.",
        "category": "Melanocytic",
        "educational_notes": "Most moles are completely harmless. The ABCDE guidelines (Asymmetry, Border irregularity, Color variation, Diameter >6mm, Evolving) serve as standard screening criteria for professional review."
    },
    2: {
        "id": "dermatofibroma",
        "name": "Dermatofibroma",
        "description": "Benign fibrous dermal nodules often occurring on lower extremities, typically firm with a characteristic 'dimple sign' upon lateral compression.",
        "category": "Mesenchymal / Dermal",
        "educational_notes": "Dermatofibromas are harmless and typically require no treatment unless irritated or cosmetically concerning."
    },
    3: {
        "id": "vascular_lesions",
        "name": "Vascular Lesions",
        "description": "Superficial blood vessel proliferations such as cherry angiomas, pyogenic granulomas, or telangiectasias.",
        "category": "Vascular",
        "educational_notes": "Vascular lesions involve localized blood vessels. Cherry angiomas are harmless, while rapidly bleeding vascular nodules should be checked by a physician."
    },
    4: {
        "id": "acne_vulgaris",
        "name": "Acne / Inflammatory Comedones",
        "description": "Follicular hyperkeratinization, microbial colonization (C. acnes), and localized follicular inflammation causing papules, pustules, or comedones.",
        "category": "Inflammatory / Follicular",
        "educational_notes": "Acne involves sebum production and follicular inflammation. Topical non-comedogenic hydration and barrier maintenance are standard supportive practices."
    },
    5: {
        "id": "eczema_and_atopic_dermatitis",
        "name": "Eczematous / Atopic Dermatitis",
        "description": "Erythematous, pruritic, dry, or desquamative cutaneous inflammation with compromised skin barrier integrity.",
        "category": "Inflammatory / Barrier Compromise",
        "educational_notes": "Eczematous skin benefits from fragrance-free barrier ceramides, gentle cleansing, and avoidance of aggressive active ingredients or allergens."
    },
    6: {
        "id": "normal_skin_or_unremarkable",
        "name": "Unremarkable / Normal Skin Surface",
        "description": "Skin surface without distinct macroscopic focal lesions, displaying regular follicular and epidermal topography.",
        "category": "Reference / Unremarkable",
        "educational_notes": "Represents baseline skin appearance. Routine sun protection and balanced hydration help preserve skin barrier health."
    }
}

NUM_CLASSES: int = len(SKIN_CLASSES)
LABEL_NAMES: list[str] = [SKIN_CLASSES[i]["name"] for i in range(NUM_CLASSES)]
LABEL_IDS: list[str] = [SKIN_CLASSES[i]["id"] for i in range(NUM_CLASSES)]
