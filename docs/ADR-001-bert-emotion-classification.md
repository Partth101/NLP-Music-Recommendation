# ADR-001: BERT for Multi-Label Emotion Classification

## Status
**Accepted**

## Date
2024

## Context

MoodTune AI requires a natural language understanding component capable of detecting multiple emotions from user-provided text. The emotion detection must be:

1. **Accurate**: High precision/recall across 17 emotion categories
2. **Fast**: Sub-100ms inference for real-time user experience
3. **Explainable**: Ability to provide word-level importance for transparency
4. **Multi-label**: Support detecting multiple co-occurring emotions

## Decision

We chose **BERT-base-uncased** as the foundation for our emotion classification model.

### Architecture
```
Input Text → BertTokenizer → BERT Encoder (12 layers) → Classification Head → Sigmoid → 17 Emotion Probabilities
```

### Key Design Choices

1. **Multi-label Classification with BCEWithLogitsLoss**
   - Each emotion is treated as an independent binary classification
   - Allows detection of overlapping emotions (e.g., "happy but nervous")

2. **Sigmoid Activation (not Softmax)**
   - Emotions are not mutually exclusive
   - Each output is an independent probability [0, 1]

3. **Confidence Thresholding**
   - Default threshold: 0.5
   - User-configurable for precision/recall trade-offs

## Alternatives Considered

### 1. RoBERTa
| Aspect | RoBERTa | Decision |
|--------|---------|----------|
| Performance | Slightly better on benchmarks | Similar for our domain |
| Size | Same as BERT-base | No advantage |
| Community Support | Good | BERT has more resources |
| **Verdict** | **Rejected** - marginal gains don't justify switching |

### 2. DistilBERT
| Aspect | DistilBERT | Decision |
|--------|------------|----------|
| Speed | 60% faster | Significant advantage |
| Size | 40% smaller | Good for deployment |
| Accuracy | 3-5% lower | Unacceptable for our use case |
| **Verdict** | **Rejected** - accuracy loss too significant |

### 3. GPT-based Classification
| Aspect | GPT-3.5/4 | Decision |
|--------|-----------|----------|
| Accuracy | High | Similar to fine-tuned BERT |
| Latency | 500ms+ API calls | Too slow for real-time |
| Cost | $0.002+ per request | Not sustainable |
| Privacy | Data sent to external API | Concern for user text |
| **Verdict** | **Rejected** - latency, cost, and privacy concerns |

### 4. Traditional ML (SVM, Random Forest)
| Aspect | Traditional ML | Decision |
|--------|----------------|----------|
| Speed | Very fast | Advantage |
| Accuracy | Lower than transformers | Significant gap |
| Context Understanding | Limited (bag-of-words) | Critical weakness |
| **Verdict** | **Rejected** - cannot capture semantic nuance |

## Consequences

### Positive
- High accuracy (84.7%) across 17 emotions
- Rich contextual understanding of text
- Compatible with SHAP for explainability
- Well-documented, extensive community support
- Pre-trained weights reduce training cost

### Negative
- Requires GPU for optimal inference speed
- 110M parameters consume significant memory
- Max 512 tokens limits very long inputs
- Fine-tuning requires labeled data

### Mitigations
| Risk | Mitigation |
|------|------------|
| GPU dependency | CPU fallback with acceptable latency |
| Memory usage | Singleton pattern ensures single model instance |
| Token limit | Truncation with warning for long inputs |
| Training data | GPT-assisted annotation pipeline |

## Technical Implementation

### Model Loading (Singleton Pattern)
```python
class ModelManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_model()
        return cls._instance
```

### Inference Pipeline
```python
def predict(self, text: str, threshold: float = 0.5):
    inputs = self._tokenizer.encode_plus(text, ...)
    with torch.no_grad():
        outputs = self._model(input_ids, attention_mask)
    scores = torch.sigmoid(outputs.logits)
    return {emotion: score for emotion, score in zip(EMOTIONS, scores)}
```

## References

1. Devlin, J., et al. (2019). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." NAACL-HLT.
2. Liu, Y., et al. (2019). "RoBERTa: A Robustly Optimized BERT Pretraining Approach." arXiv.
3. Sanh, V., et al. (2019). "DistilBERT, a distilled version of BERT." arXiv.

## Decision Makers

- **Author**: Parth Ghayal
- **Date**: 2024

---

*This ADR follows the format described by Michael Nygard in "Documenting Architecture Decisions"*
