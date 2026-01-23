"""
Emotion analysis service.

Encapsulates business logic for emotion detection and explainability,
providing a clean interface for API endpoints.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from app.ml.explainer import get_explainer
from app.ml.model_manager import ModelManager

logger = logging.getLogger(__name__)


@dataclass
class EmotionResult:
    """Result of emotion analysis."""

    emotions: dict[str, float]
    primary_emotion: str
    primary_confidence: float
    secondary_emotions: list[str]
    detected_emotions: list[str]
    confidence_level: str
    emotional_complexity: float
    explanation: Optional[str] = None
    word_importance: Optional[dict[str, float]] = None


class EmotionService:
    """
    Service for emotion analysis operations.

    Provides a high-level interface for emotion detection with optional
    SHAP-based explainability.
    """

    def __init__(self):
        self._model_manager: Optional[ModelManager] = None
        self._explainer = None

    @property
    def model_manager(self) -> ModelManager:
        """Lazy-load model manager singleton."""
        if self._model_manager is None:
            self._model_manager = ModelManager.get_instance()
        return self._model_manager

    def is_ready(self) -> bool:
        """Check if the service is ready to process requests."""
        return self.model_manager.is_loaded()

    def analyze(
        self,
        text: str,
        threshold: float = 0.5,
        include_explanation: bool = False,
    ) -> EmotionResult:
        """
        Analyze text for emotions.

        Args:
            text: Input text to analyze
            threshold: Confidence threshold for emotion detection
            include_explanation: Whether to include SHAP explanations

        Returns:
            EmotionResult with detected emotions and optional explanations

        Raises:
            RuntimeError: If model is not loaded
        """
        if not self.is_ready():
            raise RuntimeError("Emotion analysis service not ready")

        prediction = self.model_manager.predict(text, threshold=threshold)

        explanation = None
        word_importance = None

        if include_explanation:
            explainer = get_explainer(self.model_manager)
            explainer_result = explainer.explain(
                text, target_emotion=prediction["primary_emotion"]
            )
            explanation = explainer_result.get("explanation")
            word_importance = explainer_result.get("word_importance") or None

        return EmotionResult(
            emotions=prediction["emotions"],
            primary_emotion=prediction["primary_emotion"],
            primary_confidence=prediction["primary_confidence"],
            secondary_emotions=prediction["secondary_emotions"],
            detected_emotions=prediction["detected_emotions"],
            confidence_level=prediction["confidence_level"],
            emotional_complexity=prediction["emotional_complexity"],
            explanation=explanation,
            word_importance=word_importance,
        )

    def get_supported_emotions(self) -> list[str]:
        """Get list of supported emotions."""
        return self.model_manager.get_emotions_list()


# Singleton instance
_emotion_service: Optional[EmotionService] = None


def get_emotion_service() -> EmotionService:
    """Get or create the singleton emotion service instance."""
    global _emotion_service
    if _emotion_service is None:
        _emotion_service = EmotionService()
    return _emotion_service
