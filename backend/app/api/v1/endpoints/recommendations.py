"""Recommendation endpoints."""

import time
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.base import get_db
from app.models.user import User
from app.models.song import Song
from app.models.emotion_analysis import EmotionAnalysis
from app.models.recommendation import Recommendation
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationFeedback,
    RecommendationHistoryResponse,
    RecommendationHistoryItem
)
from app.schemas.song import SongResponse
from app.schemas.emotion import EmotionAnalysisResponse
from app.core.security import get_current_user_optional, get_current_user_required
from app.ml.model_manager import ModelManager
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=RecommendationResponse)
async def get_recommendation(
    request: RecommendationRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get a music recommendation based on emotional analysis of text.

    This endpoint:
    1. Analyzes the input text for emotions
    2. Matches emotions to songs in the database
    3. Returns the best matching song with explanation
    """
    start_time = time.time()

    try:
        # Get model manager
        model_manager = ModelManager.get_instance()

        if not model_manager.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model not loaded"
            )

        # Perform emotion analysis
        prediction = model_manager.predict(request.text)
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Find matching song
        song, match_score, matched_emotions = _find_best_matching_song(
            db, prediction["detected_emotions"], prediction["emotions"]
        )

        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching songs found in database"
            )

        # Generate explanation
        explanation = None
        why_this_song = None
        if request.include_explanation:
            explanation, why_this_song = _generate_recommendation_explanation(
                song, prediction["primary_emotion"], matched_emotions, match_score
            )

        # Save emotion analysis if user authenticated
        analysis = None
        if current_user and request.save_to_history:
            analysis = EmotionAnalysis(
                user_id=current_user.id,
                input_text=request.text,
                emotions=prediction["emotions"],
                primary_emotion=prediction["primary_emotion"],
                primary_confidence=prediction["primary_confidence"],
                secondary_emotions=prediction["secondary_emotions"],
                confidence_level=prediction["confidence_level"],
                emotional_complexity=prediction["emotional_complexity"],
                model_version=settings.model_version,
                processing_time_ms=processing_time_ms
            )
            db.add(analysis)
            db.flush()

        # Create recommendation record
        recommendation = Recommendation(
            user_id=current_user.id if current_user else None,
            analysis_id=analysis.id if analysis else None,
            song_id=song.id,
            match_score=match_score,
            matched_emotions=matched_emotions,
            explanation=explanation,
            why_this_song=why_this_song
        )
        db.add(recommendation)

        # Update song play count
        song.times_played = (song.times_played or 0) + 1
        song.total_matches = (song.total_matches or 0) + 1

        db.commit()
        db.refresh(recommendation)

        # Build response
        emotion_response = None
        if analysis:
            emotion_response = EmotionAnalysisResponse(
                id=analysis.id,
                emotions=prediction["emotions"],
                primary_emotion=prediction["primary_emotion"],
                primary_confidence=prediction["primary_confidence"],
                secondary_emotions=prediction["secondary_emotions"],
                detected_emotions=prediction["detected_emotions"],
                confidence_level=prediction["confidence_level"],
                emotional_complexity=prediction["emotional_complexity"],
                processing_time_ms=processing_time_ms
            )

        return RecommendationResponse(
            id=recommendation.id,
            song=SongResponse.model_validate(song),
            match_score=match_score,
            matched_emotions=matched_emotions,
            explanation=explanation,
            why_this_song=why_this_song,
            emotion_analysis=emotion_response,
            created_at=recommendation.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing recommendation"
        )


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation_by_id(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a specific recommendation by ID."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    return RecommendationResponse(
        id=recommendation.id,
        song=SongResponse.model_validate(recommendation.song),
        match_score=recommendation.match_score,
        matched_emotions=recommendation.matched_emotions or [],
        explanation=recommendation.explanation,
        why_this_song=recommendation.why_this_song,
        created_at=recommendation.created_at
    )


@router.post("/{recommendation_id}/feedback")
async def submit_feedback(
    recommendation_id: UUID,
    feedback: RecommendationFeedback,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Submit feedback for a recommendation."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    # Update feedback
    recommendation.feedback_rating = feedback.rating
    recommendation.feedback_text = feedback.feedback_text
    recommendation.was_played = 1 if feedback.was_played else 0
    recommendation.was_saved = 1 if feedback.was_saved else 0
    recommendation.feedback_at = func.now()

    # Update song average rating
    song = recommendation.song
    all_ratings = db.query(func.avg(Recommendation.feedback_rating)).filter(
        Recommendation.song_id == song.id,
        Recommendation.feedback_rating.isnot(None)
    ).scalar()
    song.average_rating = float(all_ratings) if all_ratings else None

    db.commit()

    return {"message": "Feedback submitted successfully", "rating": feedback.rating}


@router.get("/history", response_model=RecommendationHistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get user's recommendation history."""
    offset = (page - 1) * per_page

    total = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).count()

    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).order_by(Recommendation.created_at.desc()).offset(offset).limit(per_page).all()

    items = [
        RecommendationHistoryItem(
            id=r.id,
            song=SongResponse.model_validate(r.song),
            match_score=r.match_score,
            primary_emotion=r.analysis.primary_emotion if r.analysis else "Unknown",
            feedback_rating=r.feedback_rating,
            created_at=r.created_at
        )
        for r in recommendations
    ]

    return RecommendationHistoryResponse(
        recommendations=items,
        total=total,
        page=page,
        per_page=per_page
    )


def _find_best_matching_song(
    db: Session,
    detected_emotions: list[str],
    emotion_scores: dict[str, float]
) -> tuple[Optional[Song], float, list[str]]:
    """Find the best matching song based on detected emotions."""
    songs = db.query(Song).all()

    if not songs:
        return None, 0.0, []

    best_song = None
    best_score = -1
    best_matched_emotions = []

    for song in songs:
        song_emotions = song.get_emotion_list()
        matched = [e for e in detected_emotions if e in song_emotions]
        match_count = len(matched)

        # Calculate weighted score based on confidence
        weighted_score = sum(emotion_scores.get(e, 0) for e in matched)

        # Prefer songs with more matches, then by weighted score, then by least played
        if match_count > len(best_matched_emotions) or (
            match_count == len(best_matched_emotions) and weighted_score > best_score
        ) or (
            match_count == len(best_matched_emotions) and
            weighted_score == best_score and
            (best_song is None or (song.times_played or 0) < (best_song.times_played or 0))
        ):
            best_song = song
            best_score = weighted_score
            best_matched_emotions = matched

    # Normalize score
    if best_song and best_matched_emotions:
        match_score = len(best_matched_emotions) / max(len(detected_emotions), 1)
    else:
        match_score = 0.0

    return best_song, match_score, best_matched_emotions


def _generate_recommendation_explanation(
    song: Song,
    primary_emotion: str,
    matched_emotions: list[str],
    match_score: float
) -> tuple[str, list[str]]:
    """Generate explanation for why this song was recommended."""
    score_percent = int(match_score * 100)

    # Main explanation
    if len(matched_emotions) > 1:
        emotions_str = ", ".join(matched_emotions[:-1]) + f" and {matched_emotions[-1]}"
        explanation = (
            f"This track matches your emotional state with a {score_percent}% compatibility score. "
            f"It resonates with your feelings of {emotions_str}."
        )
    elif len(matched_emotions) == 1:
        explanation = (
            f"This song captures your {matched_emotions[0]} mood perfectly "
            f"with a {score_percent}% match score."
        )
    else:
        explanation = "This song was selected to complement your current mood."

    # Why this song reasons
    why_this_song = []

    if matched_emotions:
        why_this_song.append(f"Matches your {primary_emotion} mood")

    if len(matched_emotions) > 1:
        why_this_song.append(f"Covers {len(matched_emotions)} of your detected emotions")

    if song.average_rating and song.average_rating >= 4.0:
        why_this_song.append(f"Highly rated by other users ({song.average_rating:.1f}/5)")

    if song.times_played and song.times_played > 10:
        why_this_song.append("Popular choice for similar moods")

    # Default reason if none
    if not why_this_song:
        why_this_song.append("Selected to match your emotional state")

    return explanation, why_this_song
