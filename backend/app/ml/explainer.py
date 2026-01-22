"""
SHAP-based Explainability for Emotion Predictions.

Provides word-level importance scores and natural language explanations
for emotion classification results.
"""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

# Optional SHAP import - gracefully handle if not installed
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not installed. Explainability features will be limited.")


class EmotionExplainer:
    """
    Provides explainability features for emotion predictions.

    Uses SHAP (SHapley Additive exPlanations) to compute word-level
    importance scores showing which words contributed to each emotion.
    """

    def __init__(self, model_manager):
        """
        Initialize the explainer.

        Args:
            model_manager: The ModelManager instance with loaded model
        """
        self.model_manager = model_manager
        self._explainer = None
        self._initialized = False

    def _initialize_explainer(self):
        """Lazily initialize SHAP explainer."""
        if not SHAP_AVAILABLE:
            logger.warning("SHAP not available, skipping explainer initialization")
            return

        if self._initialized:
            return

        try:
            # Create prediction function for SHAP
            def predict_fn(texts):
                results = []
                for text in texts:
                    prediction = self.model_manager.predict(text)
                    # Return probabilities for all emotions
                    results.append(list(prediction["emotions"].values()))
                return np.array(results)

            # Initialize SHAP explainer with a small reference dataset
            # Using Partition explainer for text classification
            reference_texts = [
                "I am feeling okay.",
                "This is a neutral statement.",
                "Nothing special happening today."
            ]

            self._explainer = shap.Explainer(
                predict_fn,
                masker=shap.maskers.Text(self.model_manager._tokenizer),
                output_names=self.model_manager.EMOTIONS
            )
            self._initialized = True
            logger.info("SHAP explainer initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")
            self._initialized = False

    def explain(self, text: str, target_emotion: Optional[str] = None) -> dict:
        """
        Generate explanation for emotion prediction.

        Args:
            text: Input text to explain
            target_emotion: Specific emotion to explain (optional)

        Returns:
            Dictionary containing:
            - word_importance: Dict mapping words to importance scores
            - explanation: Natural language explanation
            - top_contributing_words: List of most important words
        """
        if not SHAP_AVAILABLE or not self.model_manager.is_loaded():
            return self._generate_basic_explanation(text, target_emotion)

        try:
            self._initialize_explainer()

            if not self._initialized or self._explainer is None:
                return self._generate_basic_explanation(text, target_emotion)

            # Get SHAP values
            shap_values = self._explainer([text])

            # Get prediction for context
            prediction = self.model_manager.predict(text)

            # Extract word importance
            word_importance = self._extract_word_importance(shap_values, text, target_emotion)

            # Generate natural language explanation
            explanation = self._generate_explanation(
                text,
                prediction,
                word_importance,
                target_emotion
            )

            # Get top contributing words
            top_words = sorted(
                word_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]

            return {
                "word_importance": word_importance,
                "explanation": explanation,
                "top_contributing_words": [
                    {"word": w, "importance": round(i, 3)}
                    for w, i in top_words
                ],
                "shap_available": True
            }

        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return self._generate_basic_explanation(text, target_emotion)

    def _extract_word_importance(
        self,
        shap_values,
        text: str,
        target_emotion: Optional[str] = None
    ) -> dict[str, float]:
        """Extract word-level importance from SHAP values."""
        words = text.split()
        importance = {}

        try:
            # Get values for target emotion or primary emotion
            if target_emotion and target_emotion in self.model_manager.EMOTIONS:
                emotion_idx = self.model_manager.EMOTIONS.index(target_emotion)
            else:
                # Use the emotion with highest absolute SHAP value
                emotion_idx = 0

            values = shap_values.values[0][:, emotion_idx]

            # Map SHAP values to words
            for i, word in enumerate(words[:len(values)]):
                if i < len(values):
                    importance[word] = float(values[i])

        except Exception as e:
            logger.warning(f"Error extracting word importance: {e}")

        return importance

    def _generate_explanation(
        self,
        text: str,
        prediction: dict,
        word_importance: dict,
        target_emotion: Optional[str]
    ) -> str:
        """Generate natural language explanation."""
        primary = prediction["primary_emotion"]
        confidence = prediction["primary_confidence"]

        # Get top positive and negative words
        sorted_words = sorted(
            word_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        positive_words = [w for w, s in sorted_words if s > 0][:3]
        negative_words = [w for w, s in sorted_words if s < 0][:2]

        # Build explanation
        explanation = f"Your text expresses **{primary}** ({int(confidence * 100)}% confidence). "

        if positive_words:
            words_str = ", ".join(f"'{w}'" for w in positive_words)
            explanation += f"Key words contributing to this emotion include {words_str}. "

        if prediction["secondary_emotions"]:
            secondary = prediction["secondary_emotions"][:2]
            explanation += f"Secondary emotions detected: {', '.join(secondary)}."

        return explanation

    def _generate_basic_explanation(self, text: str, target_emotion: Optional[str]) -> dict:
        """Generate basic explanation without SHAP."""
        prediction = self.model_manager.predict(text) if self.model_manager.is_loaded() else None

        if prediction:
            explanation = (
                f"Your text expresses **{prediction['primary_emotion']}** "
                f"({int(prediction['primary_confidence'] * 100)}% confidence)."
            )
            if prediction["secondary_emotions"]:
                explanation += f" Secondary emotions: {', '.join(prediction['secondary_emotions'][:3])}."
        else:
            explanation = "Unable to analyze emotions at this time."

        return {
            "word_importance": {},
            "explanation": explanation,
            "top_contributing_words": [],
            "shap_available": False
        }


# Singleton instance
_explainer_instance: Optional[EmotionExplainer] = None


def get_explainer(model_manager) -> EmotionExplainer:
    """Get or create the singleton explainer instance."""
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = EmotionExplainer(model_manager)
    return _explainer_instance
