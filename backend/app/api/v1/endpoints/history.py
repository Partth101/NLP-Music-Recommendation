"""History and statistics endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from collections import Counter

from app.db.base import get_db
from app.models.user import User
from app.models.recommendation import Recommendation
from app.models.emotion_analysis import EmotionAnalysis
from app.schemas.recommendation import HistoryStatsResponse
from app.core.security import get_current_user_required

router = APIRouter()


@router.get("/stats", response_model=HistoryStatsResponse)
async def get_history_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get statistics about user's recommendation history."""
    since_date = datetime.utcnow() - timedelta(days=days)

    # Get recommendations in time range
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.created_at >= since_date
    ).all()

    total = len(recommendations)

    # Calculate average rating
    rated = [r.feedback_rating for r in recommendations if r.feedback_rating]
    avg_rating = sum(rated) / len(rated) if rated else None

    # Get emotion analyses for emotion stats
    analyses = db.query(EmotionAnalysis).filter(
        EmotionAnalysis.user_id == current_user.id,
        EmotionAnalysis.created_at >= since_date
    ).all()

    # Count emotions
    emotion_counts = Counter()
    for analysis in analyses:
        emotion_counts[analysis.primary_emotion] += 1

    most_common = [
        {"emotion": e, "count": c}
        for e, c in emotion_counts.most_common(5)
    ]

    # Count artists
    artist_counts = Counter()
    for rec in recommendations:
        if rec.song:
            artist_counts[rec.song.artists] += 1

    favorite_artists = [
        {"artist": a, "count": c}
        for a, c in artist_counts.most_common(5)
    ]

    # Emotion trend over time (daily)
    emotion_trend = []
    current_date = since_date.date()
    end_date = datetime.utcnow().date()

    while current_date <= end_date:
        day_analyses = [
            a for a in analyses
            if a.created_at.date() == current_date
        ]

        if day_analyses:
            # Get average confidence and primary emotions for the day
            avg_confidence = sum(a.primary_confidence for a in day_analyses) / len(day_analyses)
            day_emotions = Counter(a.primary_emotion for a in day_analyses)
            dominant_emotion = day_emotions.most_common(1)[0][0] if day_emotions else None

            emotion_trend.append({
                "date": current_date.isoformat(),
                "dominant_emotion": dominant_emotion,
                "avg_confidence": round(avg_confidence, 2),
                "count": len(day_analyses)
            })

        current_date += timedelta(days=1)

    return HistoryStatsResponse(
        total_recommendations=total,
        average_rating=round(avg_rating, 2) if avg_rating else None,
        most_common_emotions=most_common,
        favorite_artists=favorite_artists,
        emotion_trend=emotion_trend
    )


@router.delete("")
async def clear_history(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Clear all recommendation history for the current user."""
    # Delete recommendations
    db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).delete()

    # Delete emotion analyses
    db.query(EmotionAnalysis).filter(
        EmotionAnalysis.user_id == current_user.id
    ).delete()

    db.commit()

    return {"message": "History cleared successfully"}
