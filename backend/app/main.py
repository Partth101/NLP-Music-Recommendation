"""MoodTune AI - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api.v1.router import api_router
from app.ml.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    # Startup: Load ML model
    logger.info("Starting MoodTune AI...")
    try:
        ModelManager.get_instance()
        logger.info(f"ML Model loaded successfully: {settings.model_version}")
    except Exception as e:
        logger.warning(f"ML Model not loaded (may need training): {e}")

    yield

    # Shutdown: Cleanup
    logger.info("Shutting down MoodTune AI...")


app = FastAPI(
    title=settings.app_name,
    description="""
    MoodTune AI - An emotion-aware music recommendation system.

    Analyze your emotions through natural language and receive personalized
    music recommendations that match your mood.

    ## Features
    - **Emotion Analysis**: BERT-based multi-label emotion detection
    - **Explainable AI**: SHAP-powered explanations for predictions
    - **Personalized Recommendations**: Learn from your feedback
    - **Voice Input**: Speak your mood instead of typing
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    model_manager = ModelManager.get_instance()
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_loaded(),
        "model_version": settings.model_version
    }
