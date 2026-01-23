# Model Card: MoodTune Emotion Classifier

## Model Details

### Overview
| Property | Value |
|----------|-------|
| **Model Name** | MoodTune Emotion Classifier |
| **Model Type** | Multi-label Text Classification |
| **Architecture** | BERT-base-uncased + Classification Head |
| **Parameters** | ~110M |
| **Framework** | PyTorch + Hugging Face Transformers |
| **License** | MIT |

### Description
A fine-tuned BERT model for multi-label emotion classification from natural language text. The model detects 17 distinct emotions simultaneously, allowing for nuanced understanding of complex emotional expressions where multiple emotions co-occur.

## Intended Use

### Primary Use Cases
- Emotion-aware music recommendation systems
- Sentiment analysis with fine-grained emotion detection
- User experience personalization based on emotional state
- Mental health applications (with appropriate clinical oversight)

### Out-of-Scope Uses
- Clinical diagnosis of mental health conditions
- High-stakes decision making without human oversight
- Analysis of non-English text
- Real-time safety-critical applications

## Training Data

### Dataset
| Property | Value |
|----------|-------|
| **Source** | Friends TV Series Dialogues (Seasons 1-10) |
| **Size** | ~10,000 labeled samples |
| **Language** | English |
| **Domain** | Conversational dialogue |

### Annotation Process
1. Raw dialogues extracted from episode transcripts
2. Preprocessing: bracket removal, duplicate filtering, length normalization
3. Multi-label emotion annotation using GPT-3.5 with human validation
4. Quality assurance through inter-annotator agreement checks

### Data Splits
| Split | Samples | Percentage |
|-------|---------|------------|
| Train | 8,000 | 80% |
| Validation | 1,000 | 10% |
| Test | 1,000 | 10% |

## Emotion Taxonomy

### 17 Supported Emotions

**Positive Emotions:**
- Happiness, Contentment, Confidence, Love, Excitement, Optimism

**Negative Emotions:**
- Sadness, Anger, Fear, Disgust, Frustration

**Complex/Neutral Emotions:**
- Neutral, Confusion, Anticipation, Nostalgia, Longing, Surprise

## Performance Metrics

### Overall Performance
| Metric | Score |
|--------|-------|
| Accuracy | 84.7% |
| F1 Score (Macro) | 81.2% |
| F1 Score (Weighted) | 85.3% |
| Inference Latency | <50ms |

### Per-Emotion Performance (Top 5)
| Emotion | Precision | Recall | F1 Score |
|---------|-----------|--------|----------|
| Happiness | 0.89 | 0.93 | 0.91 |
| Sadness | 0.85 | 0.88 | 0.86 |
| Love | 0.88 | 0.85 | 0.86 |
| Excitement | 0.84 | 0.82 | 0.83 |
| Anger | 0.82 | 0.79 | 0.80 |

## Limitations

### Known Limitations
1. **Domain Specificity**: Trained on TV dialogue; may underperform on formal text, social media, or technical content
2. **English Only**: No support for other languages
3. **Cultural Context**: Emotion expressions may vary across cultures
4. **Sarcasm/Irony**: Limited ability to detect sarcasm or ironic statements
5. **Short Text**: May have reduced accuracy on very short inputs (<5 words)

### Bias Considerations
- Training data reflects American English conversational patterns
- May have demographic biases present in the source material
- Emotion labels reflect Western psychological frameworks

## Ethical Considerations

### Potential Harms
- Misuse for surveillance or manipulation
- Over-reliance on automated emotion detection
- Privacy concerns when analyzing personal text

### Mitigations
- Model outputs include confidence scores for transparency
- SHAP explanations provide interpretability
- Designed for recommendation, not definitive classification
- Users can opt out of emotion analysis storage

## Technical Specifications

### Input Format
```python
{
    "text": str,           # Input text (max 512 tokens)
    "threshold": float,    # Detection threshold (default: 0.5)
}
```

### Output Format
```python
{
    "emotions": Dict[str, float],      # All 17 emotion scores
    "primary_emotion": str,            # Highest confidence emotion
    "primary_confidence": float,       # Confidence score [0, 1]
    "secondary_emotions": List[str],   # Other detected emotions
    "emotional_complexity": float,     # Entropy-based metric [0, 1]
}
```

### Hardware Requirements
| Configuration | Specification |
|---------------|---------------|
| **Minimum** | CPU with 4GB RAM |
| **Recommended** | NVIDIA GPU with 4GB+ VRAM |
| **Inference Speed** | ~50ms (GPU), ~200ms (CPU) |

## Citation

```bibtex
@software{moodtune_emotion_classifier,
  author = {Ghayal, Parth},
  title = {MoodTune Emotion Classifier},
  year = {2024},
  url = {https://github.com/parthmghayal/NLP-Music-Recommendation}
}
```

## Updates

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release |

---

*This model card follows the format recommended by Mitchell et al. (2019) "Model Cards for Model Reporting"*
