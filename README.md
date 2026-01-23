# MoodTune AI

[![CI/CD Pipeline](https://github.com/parthmghayal/NLP-Music-Recommendation/actions/workflows/ci.yml/badge.svg)](https://github.com/parthmghayal/NLP-Music-Recommendation/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)

An emotion-aware music recommendation system that uses BERT-based natural language processing to detect nuanced emotions from text and recommend contextually appropriate music. The system performs **multi-label classification** across 17 emotion categories with **SHAP-powered explainability**.

---

## AI Architecture

### Model Overview

| Component | Specification |
|-----------|---------------|
| **Base Model** | `bert-base-uncased` (110M parameters, 12 layers, 768 hidden units) |
| **Task** | Multi-label emotion classification |
| **Output Classes** | 17 emotions with independent sigmoid activations |
| **Loss Function** | Binary Cross-Entropy with Logits (BCEWithLogitsLoss) |
| **Inference** | Single-model serving via singleton pattern for low-latency |

### NLP Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EMOTION ANALYSIS PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Input Text                                                                 │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  TOKENIZATION (BertTokenizer)                                        │   │
│   │  • WordPiece tokenization                                            │   │
│   │  • Max sequence length: 512 tokens                                   │   │
│   │  • Special tokens: [CLS], [SEP], [PAD]                              │   │
│   │  • Attention mask generation                                         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  BERT ENCODER (12 Transformer Layers)                                │   │
│   │  • Self-attention mechanism                                          │   │
│   │  • Contextual embeddings (768-dim)                                   │   │
│   │  • [CLS] token aggregates sequence representation                    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  CLASSIFICATION HEAD                                                 │   │
│   │  • Linear layer: 768 → 17 (emotion logits)                          │   │
│   │  • Independent sigmoid activation per emotion                        │   │
│   │  • Multi-label output (emotions can co-occur)                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  POST-PROCESSING                                                     │   │
│   │  • Confidence thresholding (default: 0.5)                           │   │
│   │  • Primary/secondary emotion ranking                                 │   │
│   │  • Emotional complexity calculation (entropy-based)                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│   Emotion Scores + Explanations                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Emotional Complexity Metric

A novel metric that quantifies how diverse or focused the emotional expression is, calculated using normalized entropy:

```
Emotional Complexity = H(p) / H_max

Where:
  H(p) = -Σ p_i × log(p_i)     (Shannon entropy of emotion distribution)
  H_max = log(17)               (Maximum entropy for 17 emotions)
  p_i = σ(logit_i) / Σσ(logit_j)  (Normalized sigmoid scores)
```

- **Complexity ≈ 0**: Single dominant emotion (focused emotional state)
- **Complexity ≈ 1**: Uniform distribution across emotions (complex/mixed feelings)

### Supported Emotions (17 Classes)

```
Positive          Negative          Neutral/Complex
─────────         ─────────         ───────────────
Happiness         Sadness           Neutral
Contentment       Anger             Confusion
Confidence        Fear              Anticipation
Love              Disgust           Nostalgia
Excitement        Frustration       Longing
Optimism          Surprise
```

### Explainability (SHAP Integration)

The system uses **SHAP (SHapley Additive exPlanations)** to provide word-level importance scores:

```python
# Example output structure
{
    "word_importance": {
        "promoted": 0.234,
        "excited": 0.189,
        "I": 0.012,
        ...
    },
    "top_contributing_words": [
        {"word": "promoted", "importance": 0.234},
        {"word": "excited", "importance": 0.189}
    ],
    "explanation": "Your text expresses **Happiness** (92% confidence).
                    Key words contributing to this emotion include 'promoted', 'excited'."
}
```

### Training Methodology

| Aspect | Details |
|--------|---------|
| **Dataset** | Friends TV series dialogues (~10,000 samples) |
| **Annotation** | GPT-3.5 assisted multi-label emotion tagging |
| **Train/Val/Test Split** | 80% / 10% / 10% |
| **Optimizer** | AdamW (lr=5e-5, weight_decay=0.01) |
| **Batch Size** | 16 |
| **Epochs** | 4 (with early stopping) |
| **Hardware** | NVIDIA GPU with mixed precision (FP16) |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│                     Next.js 14 + TypeScript + Tailwind CSS                  │
│              React Server Components • Framer Motion Animations              │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ HTTPS/REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│                    FastAPI + Pydantic V2 + JWT Auth                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  /api/v1/emotions/analyze     POST   Emotion analysis with SHAP             │
│  /api/v1/recommendations      POST   Get music recommendation               │
│  /api/v1/insights/patterns    GET    AI-generated mood insights             │
│  /api/v1/auth/*               *      Authentication endpoints               │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│    PostgreSQL     │    │   ML Service      │    │      Redis        │
│    ───────────    │    │   ──────────      │    │      ─────        │
│  • User data      │    │  • BERT Model     │    │  • Session cache  │
│  • Emotions log   │    │  • SHAP Explainer │    │  • Rate limiting  │
│  • Recommendations│    │  • Singleton mgr  │    │  • Model cache    │
│  • Feedback       │    │  • GPU/CPU auto   │    │                   │
└───────────────────┘    └───────────────────┘    └───────────────────┘
```

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Core language |
| FastAPI | 0.109 | Async REST API framework |
| PyTorch | 2.1 | Deep learning framework |
| Transformers | 4.36 | BERT model loading |
| SHAP | 0.44 | Model explainability |
| SQLAlchemy | 2.0 | ORM |
| PostgreSQL | 15 | Primary database |
| Redis | 7 | Caching layer |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14 | React framework (App Router) |
| TypeScript | 5.3 | Type safety |
| Tailwind CSS | 3.4 | Utility-first styling |
| Framer Motion | 10 | Animations |
| Zustand | 4.4 | State management |
| Recharts | 2.10 | Data visualization |

### DevOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| GitHub Actions | CI/CD pipeline |
| Docker Compose | Local orchestration |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Run with Docker

```bash
git clone https://github.com/parthmghayal/NLP-Music-Recommendation.git
cd NLP-Music-Recommendation

cp .env.example .env
docker-compose up -d

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## API Examples

### Analyze Emotions

```bash
curl -X POST "http://localhost:8000/api/v1/emotions/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I just got promoted and I am so excited!", "include_explanation": true}'
```

**Response:**
```json
{
  "emotions": {
    "Happiness": 0.92,
    "Excitement": 0.87,
    "Confidence": 0.73,
    "Optimism": 0.68
  },
  "primary_emotion": "Happiness",
  "primary_confidence": 0.92,
  "secondary_emotions": ["Excitement", "Confidence"],
  "emotional_complexity": 0.58,
  "word_importance": {
    "promoted": 0.234,
    "excited": 0.189
  },
  "explanation": "Your text expresses **Happiness** (92% confidence). Key words: 'promoted', 'excited'.",
  "processing_time_ms": 47
}
```

---

## Performance

| Metric | Value |
|--------|-------|
| ML Inference Time | <50ms |
| API Response (p50) | 89ms |
| API Response (p95) | 142ms |
| Model Accuracy | 84.7% |
| F1 Score (Weighted) | 85.3% |

---

## Project Structure

```
NLP-Music-Recommendation/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST endpoints
│   │   ├── ml/                 # BERT model & SHAP explainer
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   ├── components/         # React components
│   │   └── lib/                # Utilities
│   └── package.json
├── docs/                       # Documentation
├── docker-compose.yml
└── README.md
```

---

## References

1. Devlin, J., et al. (2019). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL-HLT*.
2. Lundberg, S. M., & Lee, S. I. (2017). "A Unified Approach to Interpreting Model Predictions." *NeurIPS*.
3. Demszky, D., et al. (2020). "GoEmotions: A Dataset of Fine-Grained Emotions." *ACL*.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Parth Ghayal**

---
