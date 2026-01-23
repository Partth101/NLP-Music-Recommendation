"""Unit tests for emotion analysis functionality."""

import pytest


class TestModelManager:
    """Tests for the ModelManager singleton."""

    def test_emotions_list_defined(self):
        """Test that EMOTIONS list is properly defined."""
        from app.ml.model_manager import ModelManager

        emotions = ModelManager.EMOTIONS
        assert isinstance(emotions, list)
        assert len(emotions) == 17
        assert "Happiness" in emotions
        assert "Sadness" in emotions
        assert "Neutral" in emotions

    def test_singleton_pattern(self):
        """Test that ModelManager follows singleton pattern."""
        from app.ml.model_manager import ModelManager

        instance1 = ModelManager()
        instance2 = ModelManager()
        assert instance1 is instance2

    def test_get_emotions_list(self):
        """Test get_emotions_list returns a copy."""
        from app.ml.model_manager import ModelManager

        manager = ModelManager()
        emotions = manager.get_emotions_list()
        assert emotions == ModelManager.EMOTIONS
        # Should be a copy, not the original
        emotions.append("Test")
        assert "Test" not in ModelManager.EMOTIONS


class TestEmotionLabels:
    """Tests for emotion label consistency."""

    def test_all_emotions_present(self):
        """Test that all expected emotions are in the list."""
        from app.ml.model_manager import ModelManager

        expected_emotions = [
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
        assert ModelManager.EMOTIONS == expected_emotions

    def test_no_duplicate_emotions(self):
        """Test that there are no duplicate emotions."""
        from app.ml.model_manager import ModelManager

        emotions = ModelManager.EMOTIONS
        assert len(emotions) == len(set(emotions))
