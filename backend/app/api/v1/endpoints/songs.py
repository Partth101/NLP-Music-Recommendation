"""Song management endpoints."""

import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.base import get_db
from app.models.song import Song
from app.schemas.song import SongResponse, SongList, SongsByEmotionResponse, SongStatsResponse
from app.ml.model_manager import ModelManager

router = APIRouter()


@router.get("", response_model=SongList)
async def list_songs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    db: Session = Depends(get_db)
):
    """List all songs with pagination and optional emotion filter."""
    offset = (page - 1) * per_page

    query = db.query(Song)

    if emotion:
        # Filter songs that have this emotion
        query = query.filter(Song.emotions.contains([emotion]))

    total = query.count()
    songs = query.order_by(Song.times_played.desc()).offset(offset).limit(per_page).all()

    total_pages = (total + per_page - 1) // per_page

    return SongList(
        songs=[SongResponse.model_validate(s) for s in songs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/random", response_model=SongResponse)
async def get_random_song(db: Session = Depends(get_db)):
    """Get a random song from the database."""
    count = db.query(Song).count()

    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No songs in database"
        )

    # Random offset
    random_offset = random.randint(0, count - 1)
    song = db.query(Song).offset(random_offset).first()

    return SongResponse.model_validate(song)


@router.get("/stats", response_model=SongStatsResponse)
async def get_song_stats(db: Session = Depends(get_db)):
    """Get statistics about the song database."""
    total_songs = db.query(Song).count()
    total_plays = db.query(func.sum(Song.times_played)).scalar() or 0

    # Get emotions covered
    model_manager = ModelManager.get_instance()
    emotions_list = model_manager.get_emotions_list()

    # Get emotion distribution
    emotion_distribution = {}
    for emotion in emotions_list:
        count = db.query(Song).filter(Song.emotions.contains([emotion])).count()
        emotion_distribution[emotion] = count

    # Most played songs
    most_played = db.query(Song).order_by(Song.times_played.desc()).limit(5).all()

    return SongStatsResponse(
        total_songs=total_songs,
        total_plays=total_plays,
        emotions_covered=emotions_list,
        most_played_songs=[SongResponse.model_validate(s) for s in most_played],
        emotion_distribution=emotion_distribution
    )


@router.get("/by-emotion/{emotion}", response_model=SongsByEmotionResponse)
async def get_songs_by_emotion(
    emotion: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get songs associated with a specific emotion."""
    # Validate emotion
    model_manager = ModelManager.get_instance()
    valid_emotions = model_manager.get_emotions_list()

    if emotion not in valid_emotions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid emotion. Valid emotions: {', '.join(valid_emotions)}"
        )

    songs = db.query(Song).filter(
        Song.emotions.contains([emotion])
    ).order_by(Song.times_played.desc()).limit(limit).all()

    return SongsByEmotionResponse(
        emotion=emotion,
        songs=[SongResponse.model_validate(s) for s in songs],
        total=len(songs)
    )


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(song_id: str, db: Session = Depends(get_db)):
    """Get a specific song by ID."""
    song = db.query(Song).filter(Song.id == song_id).first()

    if not song:
        # Try by Spotify track ID
        song = db.query(Song).filter(Song.spotify_track_id == song_id).first()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    return SongResponse.model_validate(song)
