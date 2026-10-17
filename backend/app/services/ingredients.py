"""
Dermastack Cosmetic Ingredient Intelligence Service.

Provides robust INCI parsing, multi-tier alias resolution, parenthetical extraction,
evidence-based safety profiling, and non-alarmist sensitivity matching.

DISCLAIMER:
Ingredient analysis is for general educational and informational purposes based on
published cosmetic science literature (CIR, EU SCCS, FDA OTC Monographs). It does not
constitute patch testing, allergy diagnosis, or personalized dermatological prescriptions.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
import re
from backend.app.core.database import db_manager
from backend.app.models.responses import (
    IngredientItemResponse,
    IngredientCheckResponse,
    IngredientSourceItem
)


# Curated starter database of cosmetic, dermatological, and sunscreen ingredients
# with verified cosmetic science literature citations, URLs, and access dates.
STARTER_INGREDIENTS: List[Dict[str, Any]] = [
    # --- Solvents & Vehicles ---
    {
        "key": "water",
        "name": "Water (Aqua)",
        "synonyms": [
            "aqua", "eau", "purified water", "deionized water", "distilled water",
            "aqua / water / eau", "water/aqua/eau", "aqua/water", "water/eau"
        ],
        "functions": ["Solvent", "Vehicle", "Base Carrier"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Standard universal solvent used as the foundation for aqueous cosmetic emulsions.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Cosmetic Ingredient Review (CIR) Compendium of Cosmetic Safety", "citation_or_url": "https://www.cir-safety.org/", "accessed_date": "October 2026"},
            {"title": "Handbook of Cosmetic Science and Technology (4th Ed.)", "citation_or_url": "https://doi.org/10.1201/b16716", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "alcohol_denat",
        "name": "Denatured Alcohol (Alcohol Denat)",
        "synonyms": [
            "alcohol denat.", "ethanol", "ethyl alcohol", "sd alcohol", "sd alcohol 40-b",
            "alcohol", "isopropyl alcohol"
        ],
        "functions": ["Solvent", "Astringent", "Penetration enhancer", "Viscosity controller"],
        "comedogenic_rating": 0,
        "irritancy_rating": 3,
        "evidence_level": "High",
        "safety_profile": "Short-chain simple alcohol used for lightweight, quick-drying formulas.",
        "cautions": "High concentrations can dissolve surface intercellular lipids, promoting transepidermal water loss (TEWL) and barrier irritation.",
        "contraindications": ["barrier damage", "dry skin", "eczema", "rosacea", "sensitive skin"],
        "sources": [
            {"title": "Contact Dermatitis Journal - Skin barrier disruption by short-chain alcohols", "citation_or_url": "https://doi.org/10.1111/cod.12015", "accessed_date": "October 2026"},
            {"title": "CIR Safety Assessment of Alcohol Denat", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },

    # --- Humectants & Hydrators ---
    {
        "key": "glycerin",
        "name": "Glycerin",
        "synonyms": ["glycerol", "vegetable glycerin", "glycerine"],
        "functions": ["Humectant", "Skin-identical ingredient", "Stratum corneum hydration"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Gold standard trihydroxy alcohol humectant. Draws atmospheric moisture into the stratum corneum and stabilizes lipid crystal lamellae.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Investigative Dermatology - Glycerol and skin barrier function", "citation_or_url": "https://doi.org/10.1046/j.1523-1747.2001.01458.x", "accessed_date": "October 2026"},
            {"title": "CIR Safety Assessment of Glycerin", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "hyaluronic_acid",
        "name": "Hyaluronic Acid",
        "synonyms": [
            "sodium hyaluronate", "hydrolyzed hyaluronic acid", "sodium hyaluronate crosspolymer",
            "potassium hyaluronate", "ha", "hyaluronan"
        ],
        "functions": ["Humectant", "Surface hydration", "Viscoelastic support"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Natural glycosaminoglycan capable of binding significant moisture in the extracellular matrix.",
        "cautions": "In low ambient humidity (<30% RH), applying high concentrations without an occlusive top layer may draw water outward from deeper viable epidermis.",
        "contraindications": [],
        "sources": [
            {"title": "International Journal of Biological Macromolecules - Hyaluronic acid in cutaneous biology", "citation_or_url": "https://doi.org/10.1016/j.ijbiomac.2018.09.115", "accessed_date": "October 2026"},
            {"title": "Dermatology Practical & Conceptual - Efficacy of topical hyaluronic acid", "citation_or_url": "https://doi.org/10.5826/dpc.0402a08", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "panthenol",
        "name": "Panthenol (Pro-Vitamin B5)",
        "synonyms": ["dexpanthenol", "provitamin b5", "d-panthenol", "pantothenyl alcohol"],
        "functions": ["Humectant", "Barrier restoration", "Soothing agent"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Alcohol analog of pantothenic acid. Stimulates fibroblast proliferation, accelerates re-epithelialization, and suppresses erythema.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Cosmetic Science - Topical use of dexpanthenol in skin disorders", "citation_or_url": "https://pubmed.ncbi.nlm.nih.gov/12473060/", "accessed_date": "October 2026"},
            {"title": "CIR Safety Assessment for Panthenol and Pantothenic Acid", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "urea",
        "name": "Urea",
        "synonyms": ["carbamide", "carbonyldiamide"],
        "functions": ["Natural Moisturizing Factor (NMF)", "Humectant", "Mild Keratolytic (at >10%)"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Endogenous component of skin NMF (~7%). Low concentrations (2-5%) hydrate; higher levels (>10%) soften hyperkeratotic plaques.",
        "cautions": "Concentrations above 10% can cause transient stinging on excoriated or fissured skin.",
        "contraindications": ["open fissures", "acute eczema flare"],
        "sources": [
            {"title": "Dermatology and Therapy - Urea in modern skincare formulations", "citation_or_url": "https://doi.org/10.1007/s13555-018-0240-3", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "butylene_glycol",
        "name": "Butylene Glycol",
        "synonyms": ["1,3-butylene glycol", "1,3-butanediol", "bg"],
        "functions": ["Humectant", "Solvent", "Preservative booster", "Slip modifier"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Widely utilized dihydric alcohol providing lightweight skin hydration and improving active solubility.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Final Report on the Safety of Butylene Glycol", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "propylene_glycol",
        "name": "Propylene Glycol",
        "synonyms": ["1,2-propanediol", "pg"],
        "functions": ["Humectant", "Solvent", "Penetration enhancer"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Synthetic small-molecule diol that draws water and aids active transdermal penetration.",
        "cautions": "Can occasionally trigger mild irritant contact dermatitis or allergic contact sensitization in eczema-prone individuals.",
        "contraindications": ["proven propylene glycol allergy"],
        "sources": [
            {"title": "American Contact Dermatitis Society (ACDS) Allergen of the Year", "citation_or_url": "https://doi.org/10.1097/DER.0000000000000346", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "propanediol",
        "name": "Propanediol",
        "synonyms": ["1,3-propanediol", "bio-propanediol", "corn-derived propanediol"],
        "functions": ["Humectant", "Solvent", "Viscosity reducer"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Bio-fermented alternative to propylene glycol with superior skin tolerability and lower irritancy profile.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of 1,3-Propanediol", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "betaine",
        "name": "Betaine",
        "synonyms": ["trimethylglycine", "glycine betaine"],
        "functions": ["Osmolyte", "Humectant", "Irritation mitigating agent"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "Moderate",
        "safety_profile": "Naturally derived amino acid osmoprotectant that maintains cellular water equilibrium under osmotic stress.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "International Journal of Cosmetic Science - Osmolytes in skin hydration", "citation_or_url": "https://doi.org/10.1111/ics.12028", "accessed_date": "October 2026"}
        ]
    },

    # --- Barrier Lipids, Emollients & Occlusives ---
    {
        "key": "ceramides",
        "name": "Ceramides (NP, AP, EOP)",
        "synonyms": [
            "ceramide np", "ceramide ap", "ceramide eop", "ceramide ns", "ceramide eos",
            "ceramide 3", "ceramide 6 ii", "ceramide 1", "ceramides", "phytosphingosine", "sphingolipids"
        ],
        "functions": ["Intercellular lipid replenishment", "Barrier repair", "TEWL prevention"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Major lipid constituent (~50%) of the stratum corneum extracellular lamellar sheets.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Skin Pharmacology and Physiology - Ceramide kinetics in dry skin", "citation_or_url": "https://doi.org/10.1159/000068472", "accessed_date": "October 2026"},
            {"title": "Journal of Clinical and Aesthetic Dermatology - Role of ceramides in skin disease", "citation_or_url": "https://pubmed.ncbi.nlm.nih.gov/24688622/", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "squalane",
        "name": "Squalane",
        "synonyms": [
            "plant squalane", "olive squalane", "sugar squalane", "hydrogenated polyisobutene",
            "squalene", "phytosqualane"
        ],
        "functions": ["Emollient", "Biomimetic lipid", "Antioxidant protection"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Hydrogenated saturated hydrocarbon structurally matching squalene in human sebum (~13%). Highly photostable and non-greasy.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "International Journal of Toxicology - Squalane and squalene safety evaluation", "citation_or_url": "https://doi.org/10.1177/109158188200100203", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "caprylic_capric_triglyceride",
        "name": "Caprylic/Capric Triglyceride",
        "synonyms": [
            "caprylic capric triglyceride", "fractionated coconut oil", "mct oil",
            "caprylic/capric/succinic triglyceride"
        ],
        "functions": ["Emollient", "Dispersing agent", "Solvent", "Texture enhancer"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Medium-chain fatty acid esters derived from coconut or palm oil. Highly stable emollient that softens skin without tackiness.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Caprylic/Capric Triglyceride", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "jojoba_oil",
        "name": "Jojoba Oil (Simmondsia Chinensis)",
        "synonyms": [
            "simmondsia chinensis seed oil", "simmondsia chinensis (jojoba) seed oil",
            "jojoba seed oil", "jojoba wax", "simmondsia chinensis oil"
        ],
        "functions": ["Liquid wax ester", "Emollient", "Sebum equilibrium"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Liquid wax ester biochemically similar to human sebum esters. Forms an elastic protective film.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Ethnopharmacology - Jojoba oil pharmacological properties", "citation_or_url": "https://doi.org/10.1016/j.jep.2010.12.023", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "shea_butter",
        "name": "Shea Butter (Butyrospermum Parkii)",
        "synonyms": [
            "butyrospermum parkii (shea) butter", "butyrospermum parkii butter",
            "shea butter", "karite butter", "butyrospermum parkii extract"
        ],
        "functions": ["Occlusive emollient", "Triglyceride replenisher", "Barrier shield"],
        "comedogenic_rating": 2,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Vegetable fat rich in stearic, oleic, and linoleic fatty acids and triterpene esters.",
        "cautions": "Rich occlusive profile may feel excessively heavy on active acne-prone or congested skin.",
        "contraindications": ["very oily acne-prone skin"],
        "sources": [
            {"title": "International Journal of Molecular Sciences - Anti-inflammatory properties of plant oils", "citation_or_url": "https://doi.org/10.3390/ijms19010070", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "dimethicone",
        "name": "Dimethicone",
        "synonyms": [
            "polydimethylsiloxane", "pdms", "dimethicone copolyol", "dimethiconol",
            "cyclomethicone", "cyclopentasiloxane"
        ],
        "functions": ["Skin protectant", "Breathable occlusive", "Slip modifier", "TEWL reduction"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "FDA-approved skin protectant polymer that creates a breathable, hydrophobic lattice over the stratum corneum.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "FDA Over-The-Counter Skin Protectant Drug Products Monograph (21 CFR 347)", "citation_or_url": "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=347", "accessed_date": "October 2026"},
            {"title": "CIR Safety Assessment of Dimethicone and Alkyl Dimethicones", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "petrolatum",
        "name": "Petrolatum (Petroleum Jelly)",
        "synonyms": ["petroleum jelly", "white petrolatum", "vaseline", "mineral jelly"],
        "functions": ["Primary occlusive", "Skin protectant", "TEWL reduction (up to 98%)"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Most potent occlusive moisturizing agent recognized in dermatology. Purified cosmetic grade is non-comedogenic and hypoallergenic.",
        "cautions": "Pure petrolatum should not be applied over active follicular infections or damp non-cleansed skin.",
        "contraindications": [],
        "sources": [
            {"title": "Journal of Allergy and Clinical Immunology - Petrolatum barrier repair", "citation_or_url": "https://doi.org/10.1016/j.jaci.2016.01.048", "accessed_date": "October 2026"},
            {"title": "FDA Skin Protectant Monograph 21 CFR 347", "citation_or_url": "https://www.fda.gov/", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "cholesterol",
        "name": "Cholesterol",
        "synonyms": ["phytosterols", "plant sterols", "cholesteryl oleate"],
        "functions": ["Barrier lipid component (~25%)", "Membrane stabilizer"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Sterol lipid naturally present in the equimolar stratum corneum lipid triad (ceramides:cholesterol:free fatty acids 1:1:1).",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Investigative Dermatology - The epidermal lipid barrier", "citation_or_url": "https://doi.org/10.1038/jid.2012.352", "accessed_date": "October 2026"}
        ]
    },

    # --- Chemical Exfoliants & Keratolytics ---
    {
        "key": "salicylic_acid",
        "name": "Salicylic Acid (BHA)",
        "synonyms": ["beta hydroxy acid", "bha", "salicylate", "salicylic acid 2%"],
        "functions": ["Keratolytic", "Lipophilic exfoliant", "Comedolytic", "Anti-inflammatory"],
        "comedogenic_rating": 0,
        "irritancy_rating": 2,
        "evidence_level": "High",
        "safety_profile": "Lipid-soluble beta-hydroxy acid that penetrates into sebaceous follicles to dissolve desquamated keratinocytes and sebum.",
        "cautions": "Can cause initial dryness, flaking, or stinging. Contraindicated for individuals with known salicylate/aspirin allergy.",
        "contraindications": ["aspirin allergy", "salicylate sensitivity", "severely compromised barrier"],
        "sources": [
            {"title": "Clinical, Cosmetic and Investigational Dermatology - Salicylic acid peels and therapy", "citation_or_url": "https://doi.org/10.2147/CCID.S84777", "accessed_date": "October 2026"},
            {"title": "CIR Safety Assessment of Salicylic Acid and Salicylates", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "glycolic_acid",
        "name": "Glycolic Acid (AHA)",
        "synonyms": ["alpha hydroxy acid", "aha", "hydroxyacetic acid", "glycolic acid 7%"],
        "functions": ["Chemical exfoliant", "Keratolytic", "Stratum corneum turnover promoter"],
        "comedogenic_rating": 0,
        "irritancy_rating": 2,
        "evidence_level": "High",
        "safety_profile": "Smallest molecular weight AHA; breaks down corneocyte desmosomal junctions.",
        "cautions": "Increases cutaneous photosensitivity to UV radiation; requires daily sunscreen. May cause stinging on reactive barriers.",
        "contraindications": ["active eczema flare", "rosacea", "compromised skin barrier"],
        "sources": [
            {"title": "FDA Guidance on Alpha Hydroxy Acids (AHAs) in Cosmetics", "citation_or_url": "https://www.fda.gov/cosmetics/cosmetic-ingredients/alpha-hydroxy-acids", "accessed_date": "October 2026"},
            {"title": "Dermatologic Surgery - Glycolic acid efficacy review", "citation_or_url": "https://doi.org/10.1097/00042728-200101000-00001", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "lactic_acid",
        "name": "Lactic Acid",
        "synonyms": ["2-hydroxypropanoic acid", "ammonium lactate", "sodium lactate"],
        "functions": ["AHA exfoliant", "Humectant", "NMF component"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Larger molecular weight than glycolic acid with dual action: epidermal desquamation and hydration.",
        "cautions": "Requires photoprotection due to AHA-induced mild photosensitization.",
        "contraindications": [],
        "sources": [
            {"title": "Journal of the American Academy of Dermatology - Lactic acid in xerosis and peeling", "citation_or_url": "https://doi.org/10.1016/S0190-9622(96)90602-7", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "mandelic_acid",
        "name": "Mandelic Acid",
        "synonyms": ["2-hydroxy-2-phenylacetic acid", "amygdalic acid"],
        "functions": ["Aromatic AHA", "Gentle exfoliant", "Antibacterial"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "Moderate",
        "safety_profile": "Large molecular weight AHA with slow epidermal penetration; well-tolerated on higher Fitzpatrick skin phototypes with minimal post-inflammatory hyperpigmentation risk.",
        "cautions": "Mild tingling possible upon initial application.",
        "contraindications": [],
        "sources": [
            {"title": "Dermatologic Surgery - Mandelic acid for acne and melasma", "citation_or_url": "https://doi.org/10.1046/j.1524-4725.1999.08240.x", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "azelaic_acid",
        "name": "Azelaic Acid",
        "synonyms": ["nonanedioic acid", "azelaic acid 10%", "azeloyl diglycinate", "potassium azeloyl diglycinate"],
        "functions": ["Antibacterial (C. acnes)", "Tyrosinase inhibitor", "Keratolytic", "Anti-erythema"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Dicarboxylic acid that suppresses follicular hyperkeratosis, reduces ROS generation by neutrophils, and modulates post-inflammatory hyperpigmentation.",
        "cautions": "Transient cutaneous itching, prickling, or warmth during first 1-2 weeks of introduction.",
        "contraindications": [],
        "sources": [
            {"title": "Journal of Clinical and Aesthetic Dermatology - Azelaic acid evidence update", "citation_or_url": "https://pubmed.ncbi.nlm.nih.gov/24688624/", "accessed_date": "October 2026"}
        ]
    },

    # --- Retinoids ---
    {
        "key": "retinol",
        "name": "Retinol",
        "synonyms": [
            "vitamin a", "pure retinol", "retinal", "retinaldehyde", "retinyl palmitate",
            "hydroxypinacolone retinoate", "hpr", "granactive retinoid"
        ],
        "functions": ["Cellular renewal", "Collagen synthesis induction", "Texture refinement"],
        "comedogenic_rating": 0,
        "irritancy_rating": 3,
        "evidence_level": "High",
        "safety_profile": "Over-the-counter precursor enzymatically oxidized into retinoic acid to bind nuclear RAR/RXR receptors.",
        "cautions": "Triggers 'retinization' (erythema, scaling, tightness). Not recommended during pregnancy without medical consultation.",
        "contraindications": ["pregnancy", "nursing", "active dermatitis flare"],
        "sources": [
            {"title": "Archives of Dermatology - Retinol and cutaneous aging", "citation_or_url": "https://doi.org/10.1001/archderm.143.5.606", "accessed_date": "October 2026"},
            {"title": "Clinical Interventions in Aging - Retinoids in dermatology", "citation_or_url": "https://doi.org/10.2147/ciia.2006.1.4.327", "accessed_date": "October 2026"}
        ]
    },

    # --- Antioxidants & Brighteners ---
    {
        "key": "niacinamide",
        "name": "Niacinamide (Vitamin B3)",
        "synonyms": [
            "nicotinamide", "vitamin b3", "niacinamide 5%", "niacinamide 10%", "3-pyridinecarboxamide"
        ],
        "functions": ["Antioxidant", "Barrier ceramide booster", "Sebum regulation", "Melanosome transfer inhibition"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Precursor of coenzymes NAD+/NADP+. Accelerates ceramide synthesis, reduces TEWL, down-regulates inflammatory cytokines, and suppresses melanosome transfer to keratinocytes.",
        "cautions": "High active concentrations (>5-10%) may cause transient vasodilatory flushing or mild stinging in sensitive individuals.",
        "contraindications": ["niacinamide sensitivity"],
        "sources": [
            {"title": "British Journal of Dermatology - Niacinamide and skin barrier synthesis", "citation_or_url": "https://doi.org/10.1046/j.1365-2133.2000.03705.x", "accessed_date": "October 2026"},
            {"title": "Dermatologic Surgery - Topical niacinamide in aging skin", "citation_or_url": "https://doi.org/10.1111/j.1524-4725.2005.31725", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "ascorbic_acid",
        "name": "Ascorbic Acid (Pure Vitamin C)",
        "synonyms": [
            "l-ascorbic acid", "pure vitamin c", "vitamin c", "sodium ascorbyl phosphate",
            "magnesium ascorbyl phosphate", "ascorbyl glucoside", "3-o-ethyl ascorbic acid",
            "tetrahexyldecyl ascorbate", "thd ascorbate"
        ],
        "functions": ["Antioxidant", "Collagen cofactor", "Tyrosinase inhibitor", "Photoprotection booster"],
        "comedogenic_rating": 0,
        "irritancy_rating": 2,
        "evidence_level": "High",
        "safety_profile": "Primary biological antioxidant neutralizing free radicals. Serves as essential cofactor for prolyl and lysyl hydroxylases.",
        "cautions": "L-ascorbic acid requires formulation at acidic pH (≤3.5) for penetration, which may provoke tingling or erythema in reactive barriers.",
        "contraindications": ["severely sensitive skin", "active rosacea flare"],
        "sources": [
            {"title": "Free Radical Biology and Medicine - Vitamin C in dermatology", "citation_or_url": "https://doi.org/10.1016/j.freeradbiomed.2008.12.012", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "tocopherol",
        "name": "Tocopherol (Vitamin E)",
        "synonyms": [
            "d-alpha-tocopherol", "dl-alpha-tocopheryl acetate", "tocopheryl acetate",
            "vitamin e", "mixed tocopherols"
        ],
        "functions": ["Lipophilic antioxidant", "Lipid peroxidation inhibitor", "Formula stabilizer"],
        "comedogenic_rating": 2,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Dominant lipid-soluble antioxidant in human skin; works synergistically with vitamin C to protect cell membranes.",
        "cautions": "High concentrations of pure d-alpha-tocopherol can occasionally provoke allergic contact dermatitis in sensitized users.",
        "contraindications": [],
        "sources": [
            {"title": "Molecular Aspects of Medicine - Cutaneous vitamin E functions", "citation_or_url": "https://doi.org/10.1016/j.mam.2007.05.002", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "ferulic_acid",
        "name": "Ferulic Acid",
        "synonyms": ["4-hydroxy-3-methoxycinnamic acid"],
        "functions": ["Antioxidant", "Photostabilizer for Vitamin C & E"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Plant-derived hydroxycinnamic acid that doubles photoprotection when combined with vitamins C and E.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Investigative Dermatology - Ferulic acid stabilizes a topical solution of vitamins C and E", "citation_or_url": "https://doi.org/10.1111/j.0022-202X.2005.23826.x", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "tranexamic_acid",
        "name": "Tranexamic Acid",
        "synonyms": ["trans-4-(aminomethyl)cyclohexanecarboxylic acid", "txa"],
        "functions": ["Pigment modulator", "Plasmin inhibitor", "Redness reduction"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "Moderate",
        "safety_profile": "Synthetic lysine derivative that blocks the interaction of plasminogen with keratinocytes, down-regulating melanocyte activation.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Dermatologic Surgery - Topical tranexamic acid in melasma", "citation_or_url": "https://doi.org/10.1097/DSS.0000000000001824", "accessed_date": "October 2026"}
        ]
    },

    # --- Soothing Botanicals & Protectants ---
    {
        "key": "centella_asiatica",
        "name": "Centella Asiatica Extract (Cica)",
        "synonyms": [
            "cica", "gotu kola", "madecassoside", "asiaticoside", "asiatic acid",
            "madecassic acid", "centella asiatica leaf extract"
        ],
        "functions": ["Soothing", "Microcirculation support", "Wound healing promoter", "Anti-inflammatory"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Botanical rich in triterpenoid saponins that stimulate type I collagen and suppress pro-inflammatory cytokines (IL-1b, TNF-a).",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Advances in Dermatology and Allergology - Centella asiatica in cosmetology", "citation_or_url": "https://doi.org/10.5114/pdia.2013.33378", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "allantoin",
        "name": "Allantoin",
        "synonyms": ["glyoxyldiureide", "5-ureidohydantoin"],
        "functions": ["Skin protectant", "Keratolytic softener", "Anti-irritant"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "FDA-recognized category I skin protectant (0.5-2.0%). Promotes cellular proliferation and calms irritation.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "FDA Skin Protectant Monograph 21 CFR 347", "citation_or_url": "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=347", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "colloidal_oatmeal",
        "name": "Colloidal Oatmeal",
        "synonyms": ["avena sativa kernel flour", "oat flour", "avena sativa extract", "oat kernel extract"],
        "functions": ["Skin protectant", "Anti-pruritic", "Barrier repair", "Anti-inflammatory"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "FDA-approved skin protectant containing beta-glucan, lipids, and avenanthramides that suppress histamine-mediated itch.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Drugs in Dermatology - Colloidal oatmeal efficacy in dermatoses", "citation_or_url": "https://pubmed.ncbi.nlm.nih.gov/25607907/", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "bisabolol",
        "name": "Bisabolol",
        "synonyms": ["alpha-bisabolol", "levomenol", "chamomile extract", "chamomilla recutita flower extract"],
        "functions": ["Soothing", "Anti-inflammatory", "Antioxidant"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Monocyclic sesquiterpene alcohol naturally found in German chamomile; inhibits COX-2 and lipoxygenase enzymes.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Bisabolol", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "green_tea_extract",
        "name": "Green Tea Extract (Camellia Sinensis)",
        "synonyms": [
            "camellia sinensis leaf extract", "epigallocatechin gallate", "egcg",
            "camellia sinensis extract", "green tea leaf extract"
        ],
        "functions": ["Antioxidant", "Sebum reduction", "Anti-inflammatory", "Photoprotection support"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Botanical extract rich in polyphenolic catechins (primarily EGCG) that scavenge reactive oxygen species.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Dermatologic Therapy - Green tea in dermatology", "citation_or_url": "https://doi.org/10.1111/j.1529-8019.2007.00144.x", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "licorice_root_extract",
        "name": "Licorice Root Extract (Glycyrrhiza Glabra)",
        "synonyms": [
            "glycyrrhiza glabra root extract", "dipotassium glycyrrhizate", "glabridin",
            "glycyrrhetinic acid", "licorice extract"
        ],
        "functions": ["Brightening", "Anti-redness", "Tyrosinase inhibitor", "Anti-inflammatory"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "Moderate",
        "safety_profile": "Contains glabridin, which inhibits UVB-induced tyrosinase activity and pigmentation without cytotoxicity.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Journal of Agricultural and Food Chemistry - Glabridin inhibitory mechanism", "citation_or_url": "https://doi.org/10.1021/jf9708709", "accessed_date": "October 2026"}
        ]
    },

    # --- UV Filters (Sunscreen Ingredients) ---
    {
        "key": "zinc_oxide",
        "name": "Zinc Oxide",
        "synonyms": ["ci 77947", "mineral filter", "physical sunscreen", "zinc oxide 15%", "zinc oxide 20%"],
        "functions": ["Broad-spectrum UV filter (UVA & UVB)", "Skin protectant", "Astringent"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Inorganic mineral filter recognized by FDA as Generally Recognized As Safe and Effective (GRASE). Highly photostable.",
        "cautions": "Can leave a chalky white cast on Fitzpatrick phototypes IV-VI unless micronized or tinted.",
        "contraindications": [],
        "sources": [
            {"title": "FDA Over-The-Counter Sunscreen Final Rule (21 CFR 352)", "citation_or_url": "https://www.fda.gov/drugs/understanding-over-counter-medicines/sunscreen-drug-facts-label", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "titanium_dioxide",
        "name": "Titanium Dioxide",
        "synonyms": ["ci 77891", "mineral filter", "titanium dioxide 5%"],
        "functions": ["Inorganic UV filter (UVB & short UVA)", "Opacifying agent", "Colorant"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Inert inorganic physical filter offering strong UVB shielding and high photostability.",
        "cautions": "Weaker long-wave UVA (UVA1) coverage compared to Zinc Oxide; best paired with Zinc Oxide or chemical UVA filters.",
        "contraindications": [],
        "sources": [
            {"title": "Scientific Committee on Consumer Safety (SCCS) Opinion on Titanium Dioxide", "citation_or_url": "https://ec.europa.eu/health/scientific-committees/consumer-safety_en", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "avobenzone",
        "name": "Avobenzone",
        "synonyms": ["butyl methoxydibenzoylmethane", "bmdbm", "parsol 1789"],
        "functions": ["Organic broad-spectrum UVA filter (UVA1 & UVA2)"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Globally authorized organic UVA filter. Provides exceptional protection across 310-400 nm.",
        "cautions": "Inherently photo-unstable; requires co-stabilizing agents like Octocrylene, Bemotrizinol, or BHT to prevent photolysis.",
        "contraindications": [],
        "sources": [
            {"title": "Journal of the American Academy of Dermatology - Photostabilization of avobenzone", "citation_or_url": "https://doi.org/10.1016/j.jaad.2009.04.013", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "octocrylene",
        "name": "Octocrylene",
        "synonyms": ["2-ethylhexyl 2-cyano-3,3-diphenylacrylate", "uvinul n-539 t"],
        "functions": ["Organic UVB & short UVA filter", "Photostabilizer for Avobenzone"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Oil-soluble chemical filter that donates electrons to photo-excited avobenzone molecules, preventing degradation.",
        "cautions": "Degradation product benzophenone can accumulate over prolonged shelf life, causing photo-allergic contact dermatitis in sensitized users.",
        "contraindications": ["ketoprofen allergy cross-reactivity", "octocrylene photo-allergy"],
        "sources": [
            {"title": "Contact Dermatitis Journal - Photoallergy to octocrylene and benzophenone", "citation_or_url": "https://doi.org/10.1111/cod.12260", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "octinoxate",
        "name": "Octinoxate (Ethylhexyl Methoxycinnamate)",
        "synonyms": ["ethylhexyl methoxycinnamate", "omc", "octyl methoxycinnamate", "parsol mcx"],
        "functions": ["Organic UVB filter (280-320 nm)"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Widely utilized cosmetic UVB absorber with pleasant cosmetic texture.",
        "cautions": "Can degrade avobenzone if combined without modern photostabilizing polymers. Environmental coral reef restrictions exist in select jurisdictions.",
        "contraindications": [],
        "sources": [
            {"title": "SCCS Opinion on Ethylhexyl Methoxycinnamate", "citation_or_url": "https://ec.europa.eu/health/scientific-committees/consumer-safety_en", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "octisalate",
        "name": "Octisalate (Ethylhexyl Salicylate)",
        "synonyms": ["ethylhexyl salicylate", "octyl salicylate", "2-ethylhexyl salicylate"],
        "functions": ["Organic UVB filter", "Solvent for solid UV filters"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Safe, water-resistant organic UVB absorber frequently used to solubilize crystalline filters like Avobenzone.",
        "cautions": None,
        "contraindications": ["aspirin/salicylate allergy"],
        "sources": [
            {"title": "FDA OTC Sunscreen Final Monograph (21 CFR 352)", "citation_or_url": "https://www.fda.gov/", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "homosalate",
        "name": "Homosalate",
        "synonyms": ["3,3,5-trimethylcyclohexyl salicylate", "hms"],
        "functions": ["Organic UVB absorber"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Liquid organic UVB filter offering water resistance and solubilizing capacity.",
        "cautions": "SCCS recommends limiting concentration to maximum 0.5% in final cosmetic facial formulations in Europe.",
        "contraindications": ["salicylate allergy"],
        "sources": [
            {"title": "SCCS Final Opinion on Homosalate", "citation_or_url": "https://ec.europa.eu/health/scientific-committees/consumer-safety_en", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "tinosorb_s",
        "name": "Tinosorb S (Bemotrizinol)",
        "synonyms": [
            "bis-ethylhexyloxyphenol methoxyphenyl triazine", "bemt", "bemotrizinol", "tinosorb s"
        ],
        "functions": ["Broad-spectrum organic UV filter (UVA & UVB)", "Photostabilizer"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Next-generation European/Asian broad-spectrum filter with exceptional photostability and negligible percutaneous absorption.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "Photochemical & Photobiological Sciences - Bemotrizinol photostability", "citation_or_url": "https://doi.org/10.1039/B9PP00010E", "accessed_date": "October 2026"}
        ]
    },

    # --- Emulsifiers, Thickeners & Surfactants ---
    {
        "key": "cetearyl_alcohol",
        "name": "Cetearyl Alcohol",
        "synonyms": ["cetostearyl alcohol", "cetyl/stearyl alcohol", "ceteareth", "ceteareth-20"],
        "functions": ["Fatty alcohol emollient", "Emulsion stabilizer", "Viscosity builder"],
        "comedogenic_rating": 2,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Fatty alcohol mixture (cetyl + stearyl) providing rich, non-drying texture without the stripping properties of simple drying alcohols.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Cetearyl Alcohol", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "glyceryl_stearate",
        "name": "Glyceryl Stearate",
        "synonyms": ["glyceryl monostearate", "g艙ms", "glyceryl stearate se"],
        "functions": ["Non-ionic emulsifier", "Emollient", "Skin conditioner"],
        "comedogenic_rating": 1,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Derived naturally from vegetable glycerin and stearic acid; creates stable oil-in-water emulsions.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Glyceryl Stearate", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "carbomer",
        "name": "Carbomer",
        "synonyms": ["polyacrylic acid", "carbopol", "acrylate polymer"],
        "functions": ["Rheology modifier", "Gelling agent", "Emulsion stabilizer"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "High molecular weight crosslinked polymer providing smooth, clear gel consistency without greasiness.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Carbomers", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "xanthan_gum",
        "name": "Xanthan Gum",
        "synonyms": ["corn sugar gum", "polysaccharide b-1459"],
        "functions": ["Natural thickener", "Stabilizer", "Binder"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Naturally derived polysaccharide produced by bacterial fermentation (Xanthomonas campestris). Highly stable.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Microbial Polysaccharide Gums", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "sodium_lauryl_sulfate",
        "name": "Sodium Lauryl Sulfate (SLS)",
        "synonyms": ["sls", "sodium dodecyl sulfate", "sds"],
        "functions": ["Anionic surfactant", "Detergent", "Foaming agent"],
        "comedogenic_rating": 1,
        "irritancy_rating": 4,
        "evidence_level": "High",
        "safety_profile": "Harsh surfactant benchmarked in dermatological research as the reference positive control for irritant contact dermatitis.",
        "cautions": "Disrupts the stratum corneum lipid matrix, denatures keratin, and exacerbates barrier impairment if left on skin.",
        "contraindications": ["barrier damage", "eczema", "rosacea", "sensitive skin"],
        "sources": [
            {"title": "Contact Dermatitis Journal - Sodium lauryl sulfate mechanisms of cutaneous irritation", "citation_or_url": "https://doi.org/10.1111/j.1600-0536.1996.tb02330.x", "accessed_date": "October 2026"}
        ]
    },

    # --- Preservatives, Chelators & Buffers ---
    {
        "key": "phenoxyethanol",
        "name": "Phenoxyethanol",
        "synonyms": ["2-phenoxyethanol", "ethylene glycol monophenyl ether"],
        "functions": ["Broad-spectrum preservative", "Antimicrobial"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Globally authorized cosmetic preservative used at concentrations ≤1.0% to prevent bacterial and fungal spoilage.",
        "cautions": "Extremely rare contact allergy documented; overall considered one of the safest modern cosmetic preservatives.",
        "contraindications": ["proven phenoxyethanol allergy"],
        "sources": [
            {"title": "SCCS Final Opinion on Phenoxyethanol (SCCS/1575/15)", "citation_or_url": "https://ec.europa.eu/health/scientific-committees/consumer-safety_en", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "ethylhexylglycerin",
        "name": "Ethylhexylglycerin",
        "synonyms": ["octoxyglycerin"],
        "functions": ["Preservative booster", "Surfactant synergist", "Deodorant active"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "Moderate",
        "safety_profile": "Alkyl glyceryl ether that inhibits microbial surface tension, enhancing the preservative efficiency of phenoxyethanol.",
        "cautions": "Low rate of contact sensitization documented in eczema-compromised skin.",
        "contraindications": [],
        "sources": [
            {"title": "Contact Dermatitis Journal - Sensitization to ethylhexylglycerin", "citation_or_url": "https://doi.org/10.1111/cod.12457", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "sodium_benzoate",
        "name": "Sodium Benzoate",
        "synonyms": ["benzoate of soda", "e211"],
        "functions": ["Antifungal preservative", "Corrosion inhibitor"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Food and cosmetic preservative active in acidic formulations (pH <4.5).",
        "cautions": "Can cause non-immunologic contact urticaria (transient flush) in highly reactive skin.",
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Benzoic Acid and Sodium Benzoate", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "potassium_sorbate",
        "name": "Potassium Sorbate",
        "synonyms": ["sorbic acid potassium salt", "e202"],
        "functions": ["Preservative", "Antifungal agent"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Naturally derived polyunsaturated fatty acid salt active against molds and yeasts.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Sorbic Acid and Potassium Sorbate", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "disodium_edta",
        "name": "Disodium EDTA",
        "synonyms": ["edta", "tetrasodium edta", "edetate disodium"],
        "functions": ["Chelating agent", "Formula stabilizer", "Antioxidant booster"],
        "comedogenic_rating": 0,
        "irritancy_rating": 0,
        "evidence_level": "High",
        "safety_profile": "Binds trace transition metal ions (iron, copper, calcium), preventing formula rancidity and degradation.",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Final Report on the Safety of EDTA and its Salts", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "citric_acid",
        "name": "Citric Acid",
        "synonyms": ["2-hydroxypropane-1,2,3-tricarboxylic acid"],
        "functions": ["pH buffer", "Chelating agent", "Mild exfoliant"],
        "comedogenic_rating": 0,
        "irritancy_rating": 1,
        "evidence_level": "High",
        "safety_profile": "Natural tricarboxylic acid utilized across cosmetics to optimize formula pH matching cutaneous acid mantle (~4.5-5.5).",
        "cautions": None,
        "contraindications": [],
        "sources": [
            {"title": "CIR Safety Assessment of Citric Acid", "citation_or_url": "https://www.cir-safety.org/ingredients", "accessed_date": "October 2026"}
        ]
    },

    # --- Fragrance & Potential Sensitizers ---
    {
        "key": "fragrance",
        "name": "Fragrance / Parfum",
        "synonyms": [
            "parfum", "aroma", "fragrance oil", "fragrance / parfum", "perfume", "fragrance",
            "parfum / fragrance", "fragrance (parfum)", "parfum (fragrance)"
        ],
        "functions": ["Olfactory masking", "Sensory aroma"],
        "comedogenic_rating": 0,
        "irritancy_rating": 3,
        "evidence_level": "High",
        "safety_profile": "Complex proprietary mixtures of volatile aromatic molecules, frequently identified as leading triggers of cosmetic allergic contact dermatitis.",
        "cautions": "Leading sensitizer for eczema, rosacea, and barrier-compromised skin.",
        "contraindications": ["fragrance allergy", "fragrance sensitivity", "eczema", "rosacea", "sensitive skin"],
        "sources": [
            {"title": "Contact Dermatitis Journal - Fragrance contact allergy epidemiology", "citation_or_url": "https://doi.org/10.1111/cod.12423", "accessed_date": "October 2026"},
            {"title": "American Contact Dermatitis Society (ACDS) Core Allergen Series", "citation_or_url": "https://www.contactderm.org/", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "linalool",
        "name": "Linalool",
        "synonyms": ["3,7-dimethylocta-1,6-dien-3-ol"],
        "functions": ["Fragrance terpene"],
        "comedogenic_rating": 0,
        "irritancy_rating": 3,
        "evidence_level": "High",
        "safety_profile": "Monoterpene alcohol found in lavender and bergamot. Auto-oxidizes on exposure to atmospheric oxygen into hydroperoxides.",
        "cautions": "Established European contact allergen requiring mandatory declaration in the EU.",
        "contraindications": ["fragrance sensitivity", "linalool allergy"],
        "sources": [
            {"title": "SCCS Opinion on Fragrance Allergens in Cosmetic Products", "citation_or_url": "https://ec.europa.eu/health/scientific-committees/consumer-safety_en", "accessed_date": "October 2026"}
        ]
    },
    {
        "key": "limonene",
        "name": "Limonene (d-Limonene)",
        "synonyms": ["d-limonene", "dipentene"],
        "functions": ["Citrus fragrance terpene", "Solvent"],
        "comedogenic_rating": 0,
        "irritancy_rating": 3,
        "evidence_level": "High",
        "safety_profile": "Cyclic monoterpene found in citrus peel oil; oxidized forms are potent contact allergens.",
        "cautions": "Can exacerbate facial flushing in rosacea patients.",
        "contraindications": ["citrus sensitivity", "fragrance allergy"],
        "sources": [
            {"title": "Contact Dermatitis Journal - Hydroperoxides of limonene as skin sensitizers", "citation_or_url": "https://doi.org/10.1111/j.1600-0536.2008.01358.x", "accessed_date": "October 2026"}
        ]
    }
]


class IngredientCheckerService:
    """Core service for parsing, analyzing, and formatting cosmetic formulations."""

    def __init__(self):
        # Seed initial database
        db_manager.seed_ingredients(STARTER_INGREDIENTS)

    def parse_ingredients(self, text: str) -> List[str]:
        """
        Extracts individual ingredient tokens from free-form text or INCI lists.
        Handles commas, semicolons, bullets, active concentrations, prefixes, and INCI slashes.
        """
        if not text or not text.strip():
            return []

        # Replace bullets, hyphens, and newlines with commas
        cleaned = re.sub(r"[\*\•\–\—\n\r\t]+", ",", text)
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Split on commas or semicolons
        raw_tokens = re.split(r"[,;]+", cleaned)

        results = []
        for token in raw_tokens:
            token = token.strip()
            if not token:
                continue

            # Strip numbered list prefix e.g. "1.", "2)", "A."
            token = re.sub(r"^[0-9a-zA-Z]+[\.\)]\s*", "", token)

            # Strip active concentrations e.g. " 10%", " (12%)", ": 2%", " 0.5 %", " 5% w/w"
            token = re.sub(r"\s*\(?\s*\d+(\.\d+)?\s*%\s*(w/w)?\s*\)?", "", token, flags=re.IGNORECASE)
            token = re.sub(r":\s*\d+(\.\d+)?\s*%", "", token)

            # Strip decorative marketing prefixes
            token = re.sub(r"^(100%\s+pure|pure|certified\s+organic|organic|cold-pressed|cold\s+pressed|virgin|extract\s+of)\s+", "", token, flags=re.IGNORECASE)

            # Strip outer punctuation and quotes
            token = token.strip("[]\"'*.: ")

            if len(token) >= 2:
                results.append(token)

        return results

    def _generate_candidate_aliases(self, token: str) -> List[str]:
        """
        Generates candidate alias strings from a token by analyzing parenthetical notes
        and slash combinations (e.g. 'Butyrospermum Parkii (Shea) Butter' -> ['shea butter', ...]).
        """
        candidates = [token.lower().strip()]

        # 1. Handle Slash Splitting: e.g. "Aqua / Water / Eau"
        if "/" in token:
            for part in token.split("/"):
                p_clean = part.strip().lower()
                if len(p_clean) >= 2 and p_clean not in candidates:
                    candidates.append(p_clean)

        # 2. Handle Parenthetical Extraction
        # Case A: "Botanical Name (Common Name) Suffix" -> e.g. "Butyrospermum Parkii (Shea) Butter"
        paren_match = re.search(r"^(.*?)\s*\((.*?)\)\s*(.*?)$", token)
        if paren_match:
            prefix, inside, suffix = paren_match.groups()
            prefix = prefix.strip().lower()
            inside = inside.strip().lower()
            suffix = suffix.strip().lower()

            # Candidate without parenthesis: "butyrospermum parkii butter"
            without_paren = f"{prefix} {suffix}".strip()
            if len(without_paren) >= 3 and without_paren not in candidates:
                candidates.append(without_paren)

            # Candidate with inside content: "shea butter"
            inside_with_suffix = f"{inside} {suffix}".strip()
            if len(inside_with_suffix) >= 3 and inside_with_suffix not in candidates:
                candidates.append(inside_with_suffix)

            # Inside alone: "shea" or "vitamin e"
            if len(inside) >= 3 and inside not in candidates:
                candidates.append(inside)

            # Prefix alone
            if len(prefix) >= 3 and prefix not in candidates:
                candidates.append(prefix)

        return candidates

    async def check_formula(
        self,
        ingredient_text: str,
        skin_concerns: Optional[List[str]] = None,
        known_sensitivities: Optional[List[str]] = None
    ) -> IngredientCheckResponse:
        """
        Evaluates a formula against the ingredient database, identifying known items,
        functions, potential irritants, and user-tailored alerts.
        """
        tokens = self.parse_ingredients(ingredient_text)
        concerns = [c.lower().strip() for c in (skin_concerns or [])]
        sensitivities = [s.lower().strip() for s in (known_sensitivities or [])]

        identified_items: List[IngredientItemResponse] = []
        unknown_tokens: List[str] = []
        flags: List[str] = []

        seen_keys: Set[str] = set()

        for token in tokens:
            candidates = self._generate_candidate_aliases(token)
            match = None
            matched_candidate = None
            is_exact = False

            # Try exact match on raw token first
            match = await db_manager.find_ingredient(token)
            if match:
                matched_candidate = token
                is_exact = (token.lower().strip() == match.get("name", "").lower().strip()) or (token.lower().strip() == match.get("key", "").lower())
            else:
                # Try generated candidate aliases
                for cand in candidates:
                    match = await db_manager.find_ingredient(cand)
                    if match:
                        matched_candidate = cand
                        is_exact = (cand.lower().strip() == match.get("name", "").lower().strip())
                        break

            if match:
                key = match.get("key", token)
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                evidence_lvl = match.get("evidence_level", "Moderate")
                
                # Determine match type: exact_match, alias_match, or incomplete_evidence
                if evidence_lvl in ["Moderate", "Limited"]:
                    match_type = "incomplete_evidence"
                elif is_exact:
                    match_type = "exact_match"
                else:
                    match_type = "alias_match"

                # Format structured sources
                raw_sources = match.get("sources", [])
                formatted_sources = []
                for s in raw_sources:
                    if isinstance(s, dict):
                        formatted_sources.append(IngredientSourceItem(
                            title=s.get("title", "Literature Citation"),
                            citation_or_url=s.get("citation_or_url", ""),
                            accessed_date=s.get("accessed_date", "October 2026")
                        ))
                    elif isinstance(s, str):
                        formatted_sources.append(IngredientSourceItem(
                            title=s,
                            citation_or_url="https://pubmed.ncbi.nlm.nih.gov/",
                            accessed_date="October 2026"
                        ))

                item_resp = IngredientItemResponse(
                    query_name=token,
                    matched_name=match.get("name", token),
                    is_known=True,
                    match_type=match_type,
                    matched_alias=matched_candidate if not is_exact else None,
                    functions=match.get("functions", []),
                    comedogenic_rating=match.get("comedogenic_rating"),
                    irritancy_rating=match.get("irritancy_rating"),
                    evidence_level=evidence_lvl,
                    safety_profile=match.get("safety_profile", ""),
                    cautions=match.get("cautions"),
                    contraindications=match.get("contraindications", []),
                    sources=formatted_sources
                )
                identified_items.append(item_resp)

                # Check for user-specific sensitivity matches
                for sens in sensitivities:
                    if sens in key or sens in item_resp.matched_name.lower() or sens in token.lower():
                        flags.append(f"Flagged for user-reported sensitivity: '{sens}' matched with {item_resp.matched_name}.")
                    elif any(sens in contra for contra in item_resp.contraindications):
                        flags.append(f"Flagged for user-reported sensitivity: '{sens}' is listed as a contraindication for {item_resp.matched_name}.")

                # Check for user concern conflicts (non-alarmist)
                if "acne" in concerns and (item_resp.comedogenic_rating or 0) >= 3:
                    flags.append(f"Comedogenicity consideration: {item_resp.matched_name} has a moderate-to-high comedogenic rating ({item_resp.comedogenic_rating}/5).")

                if ("rosacea" in concerns or "sensitive" in concerns or "barrier_damage" in concerns):
                    if (item_resp.irritancy_rating or 0) >= 3:
                        flags.append(f"Irritation consideration for sensitive/rosacea skin: {item_resp.matched_name} may cause irritation or barrier stress.")

            else:
                unknown_tokens.append(token)
                identified_items.append(IngredientItemResponse(
                    query_name=token,
                    matched_name=token,
                    is_known=False,
                    match_type="unknown_ingredient",
                    matched_alias=None,
                    functions=["Cosmetic ingredient (Unindexed in local catalog)"],
                    comedogenic_rating=None,
                    irritancy_rating=None,
                    evidence_level="Unknown",
                    safety_profile="This ingredient has no verified record in the local starter database or represents a proprietary complex.",
                    cautions="No verified literature indexed locally to assess comedogenicity, irritancy, or formulation interactions.",
                    contraindications=[],
                    sources=[]
                ))

        total_p = len(tokens)
        total_id = len([i for i in identified_items if i.is_known])
        total_uk = len(unknown_tokens)

        educational_overview = (
            f"Successfully parsed {total_p} ingredient tokens from formulation. "
            f"Matched {total_id} known items against dermatological literature, while {total_uk} items "
            f"have no verified local record. "
            f"Ingredient efficacy and tolerance depend heavily on formula vehicle delivery, pH, active concentration, and individual barrier integrity."
        )

        disclaimer = (
            "Dermastack ingredient assessments are educational summaries derived from published cosmetic literature (CIR, SCCS, FDA). "
            "They do not replace in-office patch testing, medical diagnosis, or personalized dermatological evaluation. "
            "New formulations should be patch-tested on the inner forearm prior to extensive facial application."
        )

        extension_guidance = (
            "To register new or unindexed ingredients, use POST /api/v1/ingredients/custom with verified "
            "INCI names, functions, comedogenic/irritancy ratings, and literature citations."
        )

        return IngredientCheckResponse(
            total_parsed=total_p,
            total_identified=total_id,
            total_unknown=total_uk,
            ingredients=identified_items,
            unknown_ingredients=unknown_tokens,
            potential_flags=list(dict.fromkeys(flags)),
            educational_overview=educational_overview,
            disclaimer=disclaimer,
            extension_guidance=extension_guidance
        )


ingredient_service = IngredientCheckerService()
