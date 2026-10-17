# Dermastack — AI-Powered Skincare Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js: 14](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C.svg)](https://pytorch.org/)

**Dermastack** is an open-source, locally runnable, privacy-first skincare image feature analysis and formulation intelligence platform. It combines an experimental **Hybrid CNN + Vision Transformer (ViT)** neural network architecture with an evidence-based cosmetic ingredient evaluation engine.

---

> [!IMPORTANT]
> **Medical & Clinical Research Disclaimer**
> Dermastack is strictly an **educational and experimental platform**. It does **not** provide medical diagnoses, treatment plans, or clinical assessments. It cannot rule out skin malignancy or melanoma. Any persistent, evolving, or symptomatic skin lesions must always be evaluated in person by a board-certified dermatologist.

---

## Key Features

1. **Hybrid CNN + Vision Transformer Architecture**:
   - Residual Convolutional stages capture fine-grained local spatial textures, border contours, and pigmentation patterns.
   - Multi-Head Self-Attention (MHSA) Vision Transformer blocks model global receptive field relationships across the skin surface.
   - Dual-branch adaptive pooling and MLP fusion head.
2. **Visual Explainability (Grad-CAM)**:
   - Gradient-weighted Class Activation Mapping targeting the final convolutional stage.
   - Interactive side-by-side view and comparison overlay slider with colormap legend.
   - Explicit fallback in demo mode to prevent displaying arbitrary random weights.
3. **Calibrated Uncertainty & Rejection Policy**:
   - Out-of-distribution or ambiguous skin images are flagged as **inconclusive / uncertain** if peak confidence is below 50.0% or prediction entropy is dispersed.
4. **Cosmetic Ingredient Formulation Checker**:
   - High-throughput INCI text parser for product labels.
   - Literature-backed starter dataset covering humectants, barrier lipids, chemical exfoliants, retinoids, UV filters, preservatives, and allergens.
   - Personalized flagging against user-reported sensitivities (e.g. fragrance, essential oils) and concerns (e.g. acne comedogenicity, rosacea triggers).
5. **Privacy-First In-Memory Processing**:
   - Raw images are processed in-memory and discarded by default.
   - Optional user consent for local report history persistence.
6. **Robust Dual-Mode Execution**:
   - **Simulated Demo Mode**: Runs instantly out-of-the-box without requiring large weight downloads or external databases.
   - **Trained Model Mode**: Automatically activates when compatible weights are placed in `ml/weights/`.

---

## Technology Stack

- **Frontend**: Next.js 14 (App Router), TypeScript (Strict), Tailwind CSS, Lucide React Icons.
- **Backend**: Python 3.11+, FastAPI (Async I/O), Pydantic v2 Settings & Schemas, Uvicorn ASGI.
- **Machine Learning**: PyTorch, torchvision, Pillow, Grad-CAM.
- **Database**: MongoDB (via PyMongo with asynchronous connection handling and in-memory fallback).
- **Containerization**: Docker & Docker Compose.

---

## Directory Layout

```
dermastack/
├── .agents/
│   └── rules/
│       └── dermastack.md          # Architectural rules & coding guidelines
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── analyze.py         # Skin image upload & inference endpoint
│   │   │   ├── ingredients.py     # Formulation checker endpoint
│   │   │   ├── health.py          # System diagnostics & mode healthcheck
│   │   │   └── reports.py         # Saved report retrieval & history
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic v2 environment settings
│   │   │   ├── database.py        # MongoDB manager & in-memory demo repository
│   │   │   └── logging.py         # Centralized structured logging
│   │   ├── models/
│   │   │   ├── requests.py        # Pydantic request models
│   │   │   ├── responses.py       # Pydantic response models
│   │   │   └── documents.py       # MongoDB document serialization
│   │   ├── services/
│   │   │   ├── inference.py       # Threadpool-offloaded inference pipeline
│   │   │   ├── heatmap.py         # Grad-CAM overlay generator
│   │   │   └── ingredients.py     # Ingredient parser & cosmetic database
│   │   └── main.py                # FastAPI app entrypoint & middleware
│   ├── tests/                     # Pytest automated test suite
│   ├── requirements.txt           # Pinned backend dependencies
│   ├── Dockerfile
│   └── .env.example
├── ml/
│   ├── model.py                   # HybridSkinNet (CNN + ViT) PyTorch model
│   ├── gradcam.py                 # Grad-CAM explainer engine
│   ├── preprocessing.py           # Safe decoding, EXIF fix, & tensor prep
│   ├── labels.py                  # Skin classes, categories, & rejection limits
│   └── weights/
│       └── README.md              # Checkpoint specs & training instructions
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout & Google fonts
│   │   │   ├── page.tsx           # Main page view
│   │   │   └── globals.css        # Tailwind directives & styles
│   │   ├── components/
│   │   │   ├── Navbar.tsx         # Navigation header & live status pills
│   │   │   ├── Footer.tsx         # Medical notices & disclosures
│   │   │   ├── Dashboard.tsx      # Main tabbed workspace
│   │   │   ├── ImageUpload.tsx    # Drag-and-drop uploader with validation
│   │   │   ├── AnalysisResults.tsx# Probability cards & educational advice
│   │   │   ├── HeatmapViewer.tsx  # Comparison slider & colormap legend
│   │   │   ├── IngredientChecker.tsx # Formulation checker with presets
│   │   │   └── ReportsHistory.tsx # Saved reports list & modal inspector
│   │   └── lib/
│   │       ├── api.ts             # Centralized typed API client
│   │       └── types.ts           # TypeScript interfaces
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml             # Local multi-service orchestration
├── .gitignore
└── README.md
```

---

## Installation & Setup

### Prerequisites

- **Python**: 3.11+ (Python 3.11, 3.12, 3.13, or 3.14)
- **Node.js**: v18+ or v20+ with npm
- **MongoDB** *(Optional)*: Local MongoDB instance or MongoDB Atlas URI (application defaults to in-memory fallback if absent)

---

### Step 1: Clone & Configure Workspace

```bash
git clone <repository_url> dermastack
cd dermastack
```

---

### Step 2: Backend Setup (Python)

1. **Create and Activate Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   # Copy template
   cp backend/.env.example backend/.env
   ```
   *(On Windows PowerShell: `Copy-Item backend/.env.example backend/.env`)*

   Default configuration in `backend/.env`:
   ```ini
   APP_ENV=development
   DEMO_MODE=true
   HOST=127.0.0.1
   PORT=8000
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=dermastack
   MODEL_WEIGHTS_PATH=ml/weights/best_hybrid_skin_model.pt
   ```

4. **Run Backend Automated Tests**:
   ```bash
   pytest backend/tests -v
   ```

5. **Start the FastAPI Server**:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Backend will be live at:
   - API Root: [http://localhost:8000](http://localhost:8000)
   - Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Step 3: Frontend Setup (Next.js)

1. **Navigate to Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```
   *(On Windows systems where PowerShell script execution is restricted, use `npm.cmd install`)*

3. **Configure Frontend Environment**:
   ```bash
   cp .env.example .env.local
   ```
   *(On Windows PowerShell: `Copy-Item .env.example .env.local`)*

   Default configuration in `frontend/.env.local`:
   ```ini
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the Next.js Development Server**:
   ```bash
   npm run dev
   ```
   *(or `npm.cmd run dev` on Windows)*

5. **Open Application**:
   Navigate to [http://localhost:3000](http://localhost:3000) in your web browser.

---

## Docker Compose Setup (Optional)

To start MongoDB, FastAPI backend, and Next.js frontend together via Docker:

```bash
docker compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- MongoDB: `localhost:27017`

---

## Machine Learning Architecture & Weights

### HybridSkinNet Details

| Component | Architecture | Receptive Role |
| :--- | :--- | :--- |
| **Local Feature Extractor** | Multi-Stage Residual CNN | Boundary edges, pigment networks, follicular openings |
| **Target Conv Layer** | `cnn.stage3` (256 channels) | Layer targeted for Grad-CAM gradient backpropagation |
| **Global Sequence Attention**| 3-Layer Transformer (MHSA) | Cross-region context and spatial harmony across patches |
| **Classification Head** | Normalized Fusion MLP | 7-Class probability distribution with dropout |

### Supported Skin Classes (`ml/labels.py`)

1. `benign_keratosis_like_lesions`: Seborrheic keratoses, solar lentigines
2. `melanocytic_nevi`: Common benign moles
3. `dermatofibroma`: Fibrous dermal nodules
4. `vascular_lesions`: Cherry angiomas, telangiectasias
5. `acne_vulgaris`: Inflammatory comedones and papulopustular acne
6. `eczema_and_atopic_dermatitis`: Erythematous, dry, or barrier-compromised skin
7. `normal_skin_or_unremarkable`: Baseline unremarkable cutaneous topography

### Checkpoint Specifications

To supply trained weights, save a checkpoint dictionary to `ml/weights/best_hybrid_skin_model.pt`:
```python
import torch

checkpoint = {
    "version": "v1.0.0",
    "architecture": "HybridSkinNet",
    "num_classes": 7,
    "state_dict": model.state_dict()
}
torch.save(checkpoint, "ml/weights/best_hybrid_skin_model.pt")
```
Set `DEMO_MODE=false` in `backend/.env`. When the server boots, it verifies the state dictionary head shape `(7, 256)`. If verified, it runs full inference and generates Grad-CAM overlays.

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root service descriptor and health links |
| `GET` | `/api/v1/health` | System diagnostics, database status, inference mode |
| `POST` | `/api/v1/analyze` | Multipart image upload for feature analysis |
| `POST` | `/api/v1/ingredients/check`| JSON formulation checker against literature |
| `GET` | `/api/v1/reports` | List recent saved analysis summaries |
| `GET` | `/api/v1/reports/{report_id}` | Fetch full analysis record and Grad-CAM heatmap |

---

## Quality Assurance & Troubleshooting

### Windows Script Execution Policy
If Windows PowerShell throws:
`File ...\npm.ps1 cannot be loaded because running scripts is disabled on this system`
Run commands using the `.cmd` wrapper:
```powershell
npm.cmd install
npm.cmd run dev
npm.cmd run build
```

### MongoDB Connection Timeout
Dermastack is engineered with an immediate in-memory fallback. If MongoDB is offline, the backend logs a gentle notice and automatically uses in-memory session persistence. All features remain operational.

---

## Privacy & Security Considerations

- **No Public Deployment Without Auth**: This local build does not include public OAuth/JWT authentication. In public production environments, implement authentication, rate limiting, and HTTPS termination.
- **Image Retention Policy**: By default (`ALLOW_IMAGE_PERSISTENCE=false`), raw image bytes are processed strictly in RAM and discarded immediately after feature extraction.

---

## License

MIT License. Designed and engineered for research and educational purposes.
