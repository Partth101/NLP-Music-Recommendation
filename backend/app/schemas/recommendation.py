"""Recommendation schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.emotion import EmotionAnalysisResponse
from app.schemas.song import SongResponse


class RecommendationRequest(BaseModel):
    """Schema for recommendation request."""

    text: str = Field(
        ..., min_length=1, max_length=5000, description="Text describing your mood"
    )
    include_explanation: bool = Field(True, description="Include AI explanation")
    save_to_history: bool = Field(
        True, description="Save this recommendation to history"
    )


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""

    id: UUID
    song: SongResponse
    match_score: float = Field(..., ge=0.0, le=1.0)
    matched_emotions: list[str]

    # AI explanation
    explanation: Optional[str] = None
    why_this_song: Optional[list[str]] = None

    # Associated emotion analysis
    emotion_analysis: Optional[EmotionAnalysisResponse] = None

    # Metadata
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationFeedback(BaseModel):
    """Schema for submitting recommendation feedback."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback_text: Optional[str] = Field(None, max_length=1000)
    was_played: bool = False
    was_saved: bool = False


class RecommendationHistoryItem(BaseModel):
    """Schema for recommendation history item."""

    id: UUID
    song: SongResponse
    match_score: float
    primary_emotion: str
    feedback_rating: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationHistoryResponse(BaseModel):
    """Schema for recommendation history response."""

    recommendations: list[RecommendationHistoryItem]
    total: int
    page: int
    per_page: int


class HistoryStatsResponse(BaseModel):
    """Schema for user history statistics."""

    total_recommendations: int
    average_rating: Optional[float] = None
    most_common_emotions: list[dict[str, int]]
    favorite_artists: list[dict[str, int]]
    emotion_trend: list[dict]  # Time series data
