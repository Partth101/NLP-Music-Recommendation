"""Song model for music database."""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Song(Base):
    """Song model for storing music tracks with emotion data."""

    __tablename__ = "songs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_track_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    artists = Column(String(500), nullable=False)
    artist_id = Column(String(100), nullable=True)

    # Emotion data - stores confidence score for each of 17 emotions
    emotion_scores = Column(JSON, nullable=False, default=dict)

    # Binary emotion flags (for backward compatibility with CSV data)
    emotions = Column(ARRAY(String), nullable=True)

    # Usage statistics
    times_played = Column(Integer, default=0)
    total_matches = Column(Integer, default=0)
    average_rating = Column(Float, nullable=True)

    # Spotify audio features (optional enhancement)
    audio_features = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recommendations = relationship("Recommendation", back_populates="song")

    def __repr__(self):
        return f"<Song {self.name} by {self.artists}>"

    def get_emotion_list(self) -> list[str]:
        """Get list of emotions associated with this song."""
        if self.emotions:
            return self.emotions
        # Fall back to emotion_scores keys with score > 0.5
        return [
            emotion for emotion, score in self.emotion_scores.items() if score > 0.5
        ]

    def increment_play_count(self):
        """Increment the play count."""
        self.times_played = (self.times_played or 0) + 1
