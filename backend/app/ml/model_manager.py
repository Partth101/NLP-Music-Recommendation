"""
Singleton Model Manager for BERT Emotion Classification.

This fixes the original issue where the model was loaded on every request.
Now the model is loaded once at startup and reused for all predictions.
"""

import logging
import os
from typing import Optional

import torch
from transformers import BertForSequenceClassification, BertTokenizer

from app.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Singleton class for managing the BERT emotion classification model.

    Ensures the model is loaded only once and shared across all requests,
    significantly improving inference performance.
    """

    _instance: Optional["ModelManager"] = None
    _model: Optional[BertForSequenceClassification] = None
    _tokenizer: Optional[BertTokenizer] = None
    _device: Optional[torch.device] = None
    _loaded: bool = False

    # Emotion labels (17 emotions)
    EMOTIONS = [
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

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ModelManager":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_model()
        return cls._instance

    def _load_model(self) -> None:
        """Load the BERT model and tokenizer."""
        try:
            # Determine model path
            model_path = settings.model_path
            if not os.path.isabs(model_path):
                # Try relative to backend directory
                base_dir = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                model_path = os.path.join(base_dir, model_path)

            # Check if model exists, if not use pre-trained BERT
            if os.path.exists(model_path) and os.path.exists(
                os.path.join(model_path, "config.json")
            ):
                logger.info(f"Loading fine-tuned model from {model_path}")
                self._tokenizer = BertTokenizer.from_pretrained(model_path)
                self._model = BertForSequenceClassification.from_pretrained(model_path)
            else:
                logger.warning("Fine-tuned model not found, loading base BERT model")
                logger.warning("Run the training script to fine-tune on emotion data")
                self._tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
                self._model = BertForSequenceClassification.from_pretrained(
                    "bert-base-uncased",
                    num_labels=len(self.EMOTIONS),
                    problem_type="multi_label_classification",
                )

            # Set device
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._model.to(self._device)
            self._model.eval()

            self._loaded = True
            logger.info(f"Model loaded successfully on {self._device}")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._loaded = False
            raise

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded

    def predict(self, text: str, threshold: float = 0.5) -> dict:
        """
        Predict emotions from text with confidence scores.

        Args:
            text: Input text to analyze
            threshold: Confidence threshold for emotion detection (default 0.5)

        Returns:
            Dictionary containing:
            - emotions: Dict of all emotions with confidence scores
            - primary_emotion: Highest confidence emotion
            - secondary_emotions: Other detected emotions above threshold
            - detected_emotions: List of emotion names above threshold
            - confidence_level: Overall confidence assessment
            - raw_scores: Raw sigmoid scores for all emotions
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call _load_model() first.")

        # Tokenize input
        inputs = self._tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        input_ids = inputs["input_ids"].to(self._device)
        attention_mask = inputs["attention_mask"].to(self._device)

        # Get predictions
        with torch.no_grad():
            outputs = self._model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits

        # Apply sigmoid for multi-label classification
        scores = torch.sigmoid(logits).cpu().numpy()[0]

        # Build emotion scores dictionary
        emotion_scores = {
            emotion: float(score) for emotion, score in zip(self.EMOTIONS, scores)
        }

        # Sort by confidence
        sorted_emotions = sorted(
            emotion_scores.items(), key=lambda x: x[1], reverse=True
        )

        # Determine primary and secondary emotions
        primary_emotion = sorted_emotions[0][0]
        primary_confidence = sorted_emotions[0][1]

        detected_emotions = [
            emotion for emotion, score in emotion_scores.items() if score >= threshold
        ]

        secondary_emotions = [
            emotion for emotion in detected_emotions if emotion != primary_emotion
        ]

        # Determine confidence level
        if primary_confidence >= 0.8:
            confidence_level = "high"
        elif primary_confidence >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Calculate emotional complexity (entropy-based)
        import numpy as np

        scores_array = np.array(scores)
        scores_normalized = scores_array / (scores_array.sum() + 1e-10)
        entropy = -np.sum(scores_normalized * np.log(scores_normalized + 1e-10))
        max_entropy = np.log(len(self.EMOTIONS))
        emotional_complexity = float(entropy / max_entropy)

        return {
            "emotions": emotion_scores,
            "primary_emotion": primary_emotion,
            "primary_confidence": primary_confidence,
            "secondary_emotions": secondary_emotions,
            "detected_emotions": detected_emotions,
            "confidence_level": confidence_level,
            "emotional_complexity": emotional_complexity,
            "raw_scores": scores.tolist(),
        }

    def get_emotions_list(self) -> list[str]:
        """Get list of supported emotions."""
        return self.EMOTIONS.copy()
