"""Emotion analysis endpoints."""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import get_current_user_optional
from app.db.base import get_db
from app.ml.model_manager import ModelManager
from app.models.emotion_analysis import EmotionAnalysis
from app.models.user import User
from app.schemas.emotion import (
    EmotionAnalysisRequest,
    EmotionAnalysisResponse,
    EmotionBatchRequest,
    EmotionBatchResponse,
    SupportedEmotionsResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=EmotionAnalysisResponse)
async def analyze_emotions(
    request: EmotionAnalysisRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Analyze text for emotions using BERT-based multi-label classification.

    Returns detailed emotion analysis including:
    - Confidence scores for all 17 emotions
    - Primary and secondary emotions
    - Confidence level assessment
    - AI-generated explanation (if requested)
    - Word importance scores (SHAP values)
    """
    start_time = time.time()

    try:
        # Get model manager
        model_manager = ModelManager.get_instance()

        if not model_manager.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model not loaded. Please try again later.",
            )

        # Perform prediction
        prediction = model_manager.predict(request.text, threshold=request.threshold)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Generate explanation if requested
        explanation = None
        word_importance = None
        if request.include_explanation:
            explanation = _generate_explanation(
                prediction["primary_emotion"],
                prediction["primary_confidence"],
                prediction["secondary_emotions"],
                prediction["confidence_level"],
            )
            # TODO: Add SHAP word importance when explainer is implemented
            # word_importance = explainer.get_word_importance(request.text)

        # Save to database if user is authenticated
        analysis_id = None
        if current_user:
            analysis = EmotionAnalysis(
                user_id=current_user.id,
                input_text=request.text,
                emotions=prediction["emotions"],
                primary_emotion=prediction["primary_emotion"],
                primary_confidence=prediction["primary_confidence"],
                secondary_emotions=prediction["secondary_emotions"],
                confidence_level=prediction["confidence_level"],
                emotional_complexity=prediction["emotional_complexity"],
                explanation=explanation,
                word_importance=word_importance,
                model_version=settings.model_version,
                processing_time_ms=processing_time_ms,
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            analysis_id = analysis.id

        return EmotionAnalysisResponse(
            id=analysis_id,
            emotions=prediction["emotions"],
            primary_emotion=prediction["primary_emotion"],
            primary_confidence=prediction["primary_confidence"],
            secondary_emotions=prediction["secondary_emotions"],
            detected_emotions=prediction["detected_emotions"],
            confidence_level=prediction["confidence_level"],
            emotional_complexity=prediction["emotional_complexity"],
            explanation=explanation,
            word_importance=word_importance,
            processing_time_ms=processing_time_ms,
            model_version=settings.model_version,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing emotions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing emotion analysis",
        )


@router.post("/analyze/batch", response_model=EmotionBatchResponse)
async def analyze_emotions_batch(
    request: EmotionBatchRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Analyze multiple texts for emotions in batch."""
    start_time = time.time()

    model_manager = ModelManager.get_instance()
    if not model_manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not loaded",
        )

    results = []
    for text in request.texts:
        prediction = model_manager.predict(text, threshold=request.threshold)

        explanation = None
        if request.include_explanation:
            explanation = _generate_explanation(
                prediction["primary_emotion"],
                prediction["primary_confidence"],
                prediction["secondary_emotions"],
                prediction["confidence_level"],
            )

        results.append(
            EmotionAnalysisResponse(
                emotions=prediction["emotions"],
                primary_emotion=prediction["primary_emotion"],
                primary_confidence=prediction["primary_confidence"],
                secondary_emotions=prediction["secondary_emotions"],
                detected_emotions=prediction["detected_emotions"],
                confidence_level=prediction["confidence_level"],
                emotional_complexity=prediction["emotional_complexity"],
                explanation=explanation,
                model_version=settings.model_version,
            )
        )

    total_time = int((time.time() - start_time) * 1000)

    return EmotionBatchResponse(results=results, total_processing_time_ms=total_time)


@router.get("/supported", response_model=SupportedEmotionsResponse)
async def get_supported_emotions():
    """Get list of supported emotions."""
    model_manager = ModelManager.get_instance()
    emotions = model_manager.get_emotions_list()

    return SupportedEmotionsResponse(
        emotions=emotions,
        total=len(emotions),
        description="MoodTune AI detects 17 nuanced emotions from text using BERT-based multi-label classification",
    )


def _generate_explanation(
    primary_emotion: str,
    confidence: float,
    secondary_emotions: list[str],
    confidence_level: str,
) -> str:
    """Generate a natural language explanation of the emotion analysis."""
    confidence_percent = int(confidence * 100)

    # Build explanation
    explanation = f"Your text expresses strong **{primary_emotion}** ({confidence_percent}% confidence). "

    if secondary_emotions:
        secondary_str = ", ".join(f"**{e}**" for e in secondary_emotions[:3])
        explanation += f"Secondary emotions detected include {secondary_str}. "

    # Add confidence assessment
    if confidence_level == "high":
        explanation += "The emotional tone is clear and well-defined."
    elif confidence_level == "medium":
        explanation += "The emotional tone suggests a blend of feelings."
    else:
        explanation += "The emotional tone is subtle or mixed."

    return explanation
