"""AI-powered insights endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from collections import Counter, defaultdict

from app.db.base import get_db
from app.models.user import User
from app.models.recommendation import Recommendation
from app.models.emotion_analysis import EmotionAnalysis
from app.core.security import get_current_user_required

router = APIRouter()


@router.get("/mood-patterns")
async def get_mood_patterns(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated insights about mood patterns.

    Analyzes:
    - Weekly mood patterns
    - Time-of-day patterns
    - Emotional trends over time
    - Personalized observations
    """
    since_date = datetime.utcnow() - timedelta(days=days)

    analyses = db.query(EmotionAnalysis).filter(
        EmotionAnalysis.user_id == current_user.id,
        EmotionAnalysis.created_at >= since_date
    ).order_by(EmotionAnalysis.created_at).all()

    if not analyses:
        return {
            "has_data": False,
            "message": "Not enough data to generate insights. Keep using MoodTune AI!",
            "insights": []
        }

    insights = []

    # Analyze weekday patterns
    weekday_emotions = defaultdict(list)
    for analysis in analyses:
        weekday = analysis.created_at.strftime("%A")
        weekday_emotions[weekday].append(analysis.primary_emotion)

    # Find dominant emotion per weekday
    weekday_dominant = {}
    for day, emotions in weekday_emotions.items():
        counter = Counter(emotions)
        dominant = counter.most_common(1)[0] if counter else None
        if dominant:
            weekday_dominant[day] = {
                "emotion": dominant[0],
                "frequency": dominant[1],
                "percentage": round(dominant[1] / len(emotions) * 100)
            }

    if weekday_dominant:
        # Find the most emotional day
        most_entries = max(weekday_emotions.items(), key=lambda x: len(x[1]))
        insights.append({
            "type": "weekday_pattern",
            "title": "Your Most Active Day",
            "description": f"You tend to check in most on **{most_entries[0]}s** - you've shared your mood {len(most_entries[1])} times on this day.",
            "data": weekday_dominant
        })

    # Analyze time-of-day patterns
    hour_emotions = defaultdict(list)
    for analysis in analyses:
        hour = analysis.created_at.hour
        period = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening" if 17 <= hour < 21 else "night"
        hour_emotions[period].append(analysis.primary_emotion)

    period_insights = {}
    for period, emotions in hour_emotions.items():
        counter = Counter(emotions)
        dominant = counter.most_common(1)[0] if counter else None
        if dominant:
            period_insights[period] = {
                "emotion": dominant[0],
                "count": dominant[1]
            }

    if period_insights:
        insights.append({
            "type": "time_pattern",
            "title": "Mood by Time of Day",
            "description": "Your emotional patterns vary throughout the day.",
            "data": period_insights
        })

    # Trend analysis - compare recent week to overall
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    recent_analyses = [a for a in analyses if a.created_at >= one_week_ago]
    older_analyses = [a for a in analyses if a.created_at < one_week_ago]

    if recent_analyses and older_analyses:
        recent_positive = sum(1 for a in recent_analyses if a.primary_emotion in ["Happiness", "Excitement", "Love", "Contentment", "Optimism", "Confidence"])
        older_positive = sum(1 for a in older_analyses if a.primary_emotion in ["Happiness", "Excitement", "Love", "Contentment", "Optimism", "Confidence"])

        recent_ratio = recent_positive / len(recent_analyses)
        older_ratio = older_positive / len(older_analyses)
        change = recent_ratio - older_ratio

        if abs(change) > 0.1:
            direction = "more positive" if change > 0 else "more reflective"
            percentage = abs(int(change * 100))
            insights.append({
                "type": "trend",
                "title": "Recent Mood Trend",
                "description": f"Your mood has been **{percentage}% {direction}** this week compared to before.",
                "data": {
                    "recent_positive_ratio": round(recent_ratio, 2),
                    "older_positive_ratio": round(older_ratio, 2),
                    "change": round(change, 2)
                }
            })

    # Emotional complexity insight
    avg_complexity = sum(a.emotional_complexity or 0 for a in analyses) / len(analyses)
    if avg_complexity > 0.6:
        insights.append({
            "type": "complexity",
            "title": "Rich Emotional Expression",
            "description": "You experience a diverse range of emotions - your emotional complexity score is above average!",
            "data": {"complexity_score": round(avg_complexity, 2)}
        })

    return {
        "has_data": True,
        "total_analyses": len(analyses),
        "period_days": days,
        "insights": insights
    }


@router.get("/music-taste")
async def get_music_taste_profile(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Get insights about user's music taste based on recommendations.

    Analyzes:
    - Preferred genres/artists
    - Emotional music preferences
    - Listening patterns
    """
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).all()

    if len(recommendations) < 5:
        return {
            "has_data": False,
            "message": "Get at least 5 recommendations to see your music taste profile!",
            "profile": None
        }

    # Analyze artists
    artist_counts = Counter()
    for rec in recommendations:
        if rec.song:
            artist_counts[rec.song.artists] += 1

    top_artists = artist_counts.most_common(5)

    # Analyze emotions in music choices
    music_emotions = Counter()
    for rec in recommendations:
        for emotion in (rec.matched_emotions or []):
            music_emotions[emotion] += 1

    top_music_emotions = music_emotions.most_common(5)

    # Analyze highly rated recommendations
    good_recs = [r for r in recommendations if r.feedback_rating and r.feedback_rating >= 4]
    bad_recs = [r for r in recommendations if r.feedback_rating and r.feedback_rating <= 2]

    preferred_emotions = Counter()
    for rec in good_recs:
        for emotion in (rec.matched_emotions or []):
            preferred_emotions[emotion] += 1

    avoided_emotions = Counter()
    for rec in bad_recs:
        for emotion in (rec.matched_emotions or []):
            avoided_emotions[emotion] += 1

    # Build profile
    profile = {
        "top_artists": [{"artist": a, "count": c} for a, c in top_artists],
        "music_emotion_preferences": [{"emotion": e, "count": c} for e, c in top_music_emotions],
        "preferred_emotions": [{"emotion": e, "count": c} for e, c in preferred_emotions.most_common(3)],
        "less_preferred_emotions": [{"emotion": e, "count": c} for e, c in avoided_emotions.most_common(3)],
        "total_recommendations": len(recommendations),
        "average_match_score": round(sum(r.match_score for r in recommendations) / len(recommendations), 2),
        "feedback_count": len([r for r in recommendations if r.feedback_rating])
    }

    # Generate description
    if top_artists:
        fav_artist = top_artists[0][0]
        profile["description"] = f"Based on {len(recommendations)} recommendations, you gravitate towards artists like **{fav_artist}**. "
    else:
        profile["description"] = ""

    if top_music_emotions:
        top_emotion = top_music_emotions[0][0]
        profile["description"] += f"You tend to seek out music that evokes **{top_emotion}**."

    return {
        "has_data": True,
        "profile": profile
    }
