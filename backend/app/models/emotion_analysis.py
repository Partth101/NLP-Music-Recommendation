"""Emotion Analysis model for storing analysis results."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class EmotionAnalysis(Base):
    """Model for storing emotion analysis results."""

    __tablename__ = "emotion_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Input
    input_text = Column(Text, nullable=False)

    # Analysis results
    emotions = Column(JSON, nullable=False)  # Full emotion scores dict
    primary_emotion = Column(String(50), nullable=False)
    primary_confidence = Column(Float, nullable=False)
    secondary_emotions = Column(JSON, default=list)  # List of secondary emotions
    confidence_level = Column(String(20), nullable=False)  # high/medium/low
    emotional_complexity = Column(Float, nullable=True)

    # Explainability
    explanation = Column(Text, nullable=True)
    word_importance = Column(JSON, nullable=True)  # SHAP values

    # Metadata
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="emotion_analyses")
    recommendation = relationship("Recommendation", back_populates="analysis", uselist=False)

    def __repr__(self):
        return f"<EmotionAnalysis {self.primary_emotion} ({self.primary_confidence:.2f})>"
