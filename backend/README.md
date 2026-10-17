# Dermastack FastAPI Backend

The backend for Dermastack provides asynchronous RESTful endpoints for dermatological image feature extraction, cosmetic ingredient formulation analysis, health diagnostics, and report retrieval.

## Architecture & Directory Layout

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── health.py        # System health and mode check
│   │   ├── analyze.py       # Skin image upload and inference
│   │   ├── ingredients.py   # Ingredient evaluation engine
│   │   └── reports.py       # Stored analysis retrieval
│   ├── core/
│   │   ├── config.py        # Pydantic v2 settings
│   │   ├── database.py      # MongoDB lifecycle & demo persistence fallback
│   │   └── logging.py       # Structured logging
│   ├── models/
│   │   ├── requests.py      # Request schemas
│   │   ├── responses.py     # Response schemas
│   │   └── documents.py     # MongoDB document builders
│   ├── services/
│   │   ├── inference.py     # Execution pipeline & threadpool offloading
│   │   ├── heatmap.py       # Grad-CAM overlay generation
│   │   └── ingredients.py   # Ingredient parsing & literature database
│   └── main.py              # Application entrypoint & middleware
├── tests/                   # Automated pytest suite
├── requirements.txt         # Pinned Python dependencies
└── .env.example             # Configuration template
```

## Quick Start (Local Run)

1. **Activate Virtual Environment** (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment**:
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```

4. **Start Backend Server**:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Access Interactive API Docs**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Running Backend Automated Tests

```powershell
pytest backend/tests -v
```
