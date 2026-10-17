"""
Dermastack FastAPI Application Main Entrypoint.

Handles application lifecycle, CORS, routing, logging, and error handling.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.core.database import db_manager
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.analyze import router as analyze_router
from backend.app.api.v1.ingredients import router as ingredients_router
from backend.app.api.v1.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and graceful shutdown."""
    setup_logging()
    logger.info("Initializing %s [%s]...", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Environment: %s | Demo Mode: %s", settings.APP_ENV, settings.DEMO_MODE)

    # Initialize Database connection
    db_manager.connect()

    yield

    # Clean shutdown
    logger.info("Shutting down %s...", settings.APP_NAME)
    db_manager.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Skincare Analysis & Ingredient Intelligence Platform (Experimental & Educational).",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        errors.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "status_code": 422,
            "message": "Input validation failed.",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "An internal server error occurred. Please try again later."
        }
    )


# Register API v1 Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(analyze_router, prefix="/api/v1")
app.include_router(ingredients_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root info endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
