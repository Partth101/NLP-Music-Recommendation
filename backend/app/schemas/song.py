"""Song schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SongBase(BaseModel):
    """Base song schema."""

    name: str
    artists: str
    spotify_track_id: str


class SongResponse(BaseModel):
    """Schema for song response."""

    id: UUID
    spotify_track_id: str
    name: str
    artists: str
    artist_id: Optional[str] = None
    emotion_scores: dict[str, float] = Field(default_factory=dict)
    emotions: Optional[list[str]] = None
    times_played: int = 0
    average_rating: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SongList(BaseModel):
    """Schema for paginated song list."""

    songs: list[SongResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class SongsByEmotionResponse(BaseModel):
    """Schema for songs filtered by emotion."""

    emotion: str
    songs: list[SongResponse]
    total: int


class SongStatsResponse(BaseModel):
    """Schema for song database statistics."""

    total_songs: int
    total_plays: int
    emotions_covered: list[str]
    most_played_songs: list[SongResponse]
    emotion_distribution: dict[str, int]
