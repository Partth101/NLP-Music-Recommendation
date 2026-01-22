"""Database initialization and CSV data migration."""

import logging
import os

import pandas as pd
from sqlalchemy.orm import Session

from app.db.base import Base, SessionLocal, engine
from app.models.song import Song

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def migrate_songs_from_csv(csv_path: str, db: Session) -> int:
    """
    Migrate songs from CSV file to database.

    Args:
        csv_path: Path to processed_songs.csv
        db: Database session

    Returns:
        Number of songs migrated
    """
    if not os.path.exists(csv_path):
        logger.warning(f"CSV file not found: {csv_path}")
        return 0

    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Found {len(df)} songs in CSV")

        # Expected emotion columns
        emotion_columns = [
            "Happiness",
            "Contentment",
            "Confidence",
            "Neutral",
            "Sadness",
            "Anger",
            "Fear",
            "Surprise",
            "Disgust",
            "Love",
            "Excitement",
            "Anticipation",
            "Nostalgia",
            "Confusion",
            "Frustration",
            "Longing",
            "Optimism",
        ]

        migrated = 0
        for _, row in df.iterrows():
            # Check if song already exists
            existing = (
                db.query(Song)
                .filter(Song.spotify_track_id == str(row.get("Track_ID", "")))
                .first()
            )

            if existing:
                continue

            # Extract emotions
            emotions = []
            emotion_scores = {}

            for emotion in emotion_columns:
                if emotion in row and pd.notna(row[emotion]):
                    score = float(row[emotion])
                    emotion_scores[emotion] = score
                    if score > 0.5:  # Binary threshold
                        emotions.append(emotion)

            # Create song record
            song = Song(
                spotify_track_id=str(row.get("Track_ID", "")),
                name=str(row.get("Song Name", "Unknown")),
                artists=str(row.get("Artists", "Unknown")),
                artist_id=(
                    str(row.get("Artist_ID", ""))
                    if pd.notna(row.get("Artist_ID"))
                    else None
                ),
                emotions=emotions,
                emotion_scores=emotion_scores,
                times_played=(
                    int(row.get("Times_played", 0))
                    if pd.notna(row.get("Times_played"))
                    else 0
                ),
            )

            db.add(song)
            migrated += 1

        db.commit()
        logger.info(f"Migrated {migrated} songs to database")
        return migrated

    except Exception as e:
        logger.error(f"Error migrating songs: {e}")
        db.rollback()
        return 0


def init_database():
    """Initialize database with tables and seed data."""
    # Create tables
    create_tables()

    # Migrate CSV data
    db = SessionLocal()
    try:
        # Find CSV file
        possible_paths = [
            "/app/data/processed_songs.csv",  # Docker container path
            "./data/processed_songs.csv",  # Local backend/data path
            "../data/processed_songs.csv",  # Relative path
        ]

        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break

        if csv_path:
            count = migrate_songs_from_csv(csv_path, db)
            logger.info(f"Database initialized with {count} songs")
        else:
            logger.warning("No CSV file found for migration")

    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
