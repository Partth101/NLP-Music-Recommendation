"""Recommendation model for storing music recommendations."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Recommendation(Base):
    """Model for storing music recommendations and user feedback."""

    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("emotion_analyses.id", ondelete="SET NULL"), nullable=True)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)

    # Match details
    match_score = Column(Float, nullable=False)
    matched_emotions = Column(JSON, default=list)  # List of matching emotions

    # AI explanation
    explanation = Column(Text, nullable=True)
    why_this_song = Column(JSON, nullable=True)  # List of reasons

    # User feedback
    feedback_rating = Column(Integer, nullable=True)  # 1-5 stars
    feedback_text = Column(Text, nullable=True)
    was_played = Column(Integer, default=0)  # Play count
    was_saved = Column(Integer, default=0)  # Save/like flag

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    feedback_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    analysis = relationship("EmotionAnalysis", back_populates="recommendation")
    song = relationship("Song", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation {self.id} - Score: {self.match_score:.2f}>"
