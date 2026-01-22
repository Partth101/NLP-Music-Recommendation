"""Emotion analysis schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EmotionAnalysisRequest(BaseModel):
    """Schema for emotion analysis request."""

    text: str = Field(
        ..., min_length=1, max_length=5000, description="Text to analyze for emotions"
    )
    include_explanation: bool = Field(
        True, description="Include AI explanation of the analysis"
    )
    threshold: float = Field(
        0.5, ge=0.0, le=1.0, description="Confidence threshold for emotion detection"
    )


class EmotionInfo(BaseModel):
    """Schema for individual emotion info."""

    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_detected: bool


class EmotionAnalysisResponse(BaseModel):
    """Schema for emotion analysis response."""

    id: Optional[UUID] = None

    # Core results
    emotions: dict[str, float] = Field(
        ..., description="All emotions with confidence scores"
    )
    primary_emotion: str = Field(..., description="Highest confidence emotion")
    primary_confidence: float = Field(..., ge=0.0, le=1.0)
    secondary_emotions: list[str] = Field(
        default_factory=list, description="Other detected emotions"
    )
    detected_emotions: list[str] = Field(
        ..., description="All emotions above threshold"
    )

    # Analysis metadata
    confidence_level: str = Field(
        ..., description="Overall confidence: high/medium/low"
    )
    emotional_complexity: float = Field(
        ..., ge=0.0, le=1.0, description="Measure of emotion diversity"
    )

    # Explainability
    explanation: Optional[str] = Field(None, description="Natural language explanation")
    word_importance: Optional[dict[str, float]] = Field(
        None, description="Word-level importance scores"
    )

    # Metadata
    processing_time_ms: Optional[int] = None
    model_version: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmotionBatchRequest(BaseModel):
    """Schema for batch emotion analysis."""

    texts: list[str] = Field(
        ..., min_length=1, max_length=10, description="List of texts to analyze"
    )
    include_explanation: bool = False
    threshold: float = 0.5


class EmotionBatchResponse(BaseModel):
    """Schema for batch emotion analysis response."""

    results: list[EmotionAnalysisResponse]
    total_processing_time_ms: int


class SupportedEmotionsResponse(BaseModel):
    """Schema for supported emotions list."""

    emotions: list[str]
    total: int
    description: str = "MoodTune AI detects 17 nuanced emotions from text"
