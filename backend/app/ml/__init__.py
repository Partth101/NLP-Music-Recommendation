"""
Machine Learning module for MoodTune AI.

This module provides the core ML capabilities:
- BERT-based multi-label emotion classification
- SHAP-based model explainability
- Efficient singleton model management
"""

from app.ml.explainer import EmotionExplainer, get_explainer
from app.ml.model_manager import ModelManager

__all__ = ["ModelManager", "EmotionExplainer", "get_explainer"]
