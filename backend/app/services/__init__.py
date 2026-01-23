"""
Business logic services for MoodTune AI.

This module contains service classes that encapsulate business logic,
separating it from API endpoints and data access layers.
"""

from app.services.emotion_service import EmotionService

__all__ = ["EmotionService"]
