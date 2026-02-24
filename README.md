# Keneya Lens - Offline Medical AI for Community Health Workers

> **"Keneya"** means "health" in Bambara, the most widely spoken language in Mali

Keneya Lens is an **offline-first medical assistant** designed to help Community Health Workers (CHWs) with symptom triage and medical guidance. Built for the **MedGemma Impact Challenge 2026**, it combines multiple HAI-DEF models with RAG (Retrieval-Augmented Generation) for comprehensive medical support.

## 🏆 MedGemma Impact Challenge

This project demonstrates the full potential of Google's Health AI Developer Foundations (HAI-DEF):

| Model | Use Case |
|-------|----------|
| **MedGemma 4B** | Text-based symptom triage and medical reasoning |
| **CXR Foundation** | Chest X-ray analysis |
| **Derm Foundation** | Skin lesion analysis |
| **Path Foundation** | Pathology image analysis |

## 🏥 Features

### Core Capabilities
- **Offline Operation**: Runs entirely locally without internet connectivity
- **Multi-Model Support**: Intelligent routing between HAI-DEF models
- **Medical Image Analysis**: CXR, skin lesion, and pathology support
- **RAG Pipeline**: Context-aware responses from local medical guidelines
- **Safety-First Design**: Built-in ethical guidelines and professional referral

### Technical Features
- **Streamlit UI**: User-friendly interface for symptom queries
- **FastAPI Backend**: Robust API for model inference
- **8-bit Quantization**: Efficient memory usage for resource-limited devices
- **Query Logging**: Audit trail for all medical queries

## 📁 Project Structure

```
Keneya Lens/
├── app/
│   ├── medgemma_engine.py      # Core engine with HAI-DEF integration
│   ├── model_registry.py       # Multi-model management
│   ├── foundation_models.py    # CXR, Derm, Path model handlers
│   ├── api.py                  # FastAPI backend
│   └── streamlit_app.py        # Streamlit UI
├── utils/
│   ├── pdf_processor.py        # PDF processing
│   ├── image_processor.py      # Medical image processing
│   ├── validators.py           # Input validation
│   └── query_logger.py         # Query logging
├── scripts/
│   ├── benchmark.py            # Performance benchmarking
│   ├── setup_check.py          # Installation verification
│   └── start_all.py            # Launch all services
├── notebooks/
│   └── fine_tuning_guide.py    # MedGemma fine-tuning tutorial
├── docs/
│   ├── COMPETITION_WRITEUP.md  # 3-page submission writeup
│   ├── IMPACT_STORY.md         # User journey and impact metrics
│   ├── PERFORMANCE_ANALYSIS.md # Benchmark results
│   ├── DEPLOYMENT_CHALLENGES.md # Deployment guide
│   └── ...
├── data/
│   ├── chroma_db/              # Vector database
│   └── uploads/                # Uploaded files
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- 8GB+ RAM (16GB recommended)
- GPU optional but recommended
- 10GB+ free disk space

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set HuggingFace token (required for MedGemma)
export HUGGINGFACE_TOKEN=your_token_here

# 4. Start the application
python scripts/start_all.py
```

### Access the Application

- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📚 Usage

### Symptom Triage

```python
from app import MedGemmaEngine

engine = MedGemmaEngine()
result = engine.query_symptoms(
    "Child, 4 years old, with fever for 3 days, cough, and difficulty breathing"
)
print(result['response'])
```

### Medical Image Analysis

```python
from app import MedGemmaEngine

engine = MedGemmaEngine()
result = engine.analyze_medical_image(
    image_path="chest_xray.jpg",
    query="Analyze this chest X-ray for signs of pneumonia",
    image_type="xray"
)
print(result['interpretation'])
```

### Multi-Model Queries

```python
from app import MultiModelEngine

engine = MultiModelEngine()

# Automatic routing to appropriate model
result = engine.query(
    "Patient has a suspicious skin lesion on forearm",
    image_path="skin_lesion.jpg"
)
# Routes to Derm Foundation automatically
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
HUGGINGFACE_TOKEN=your_hf_token

# Optional
MEDGEMMA_MODEL=google/medgemma-4b-it
DEVICE=auto  # auto, cpu, cuda
API_PORT=8000
STREAMLIT_PORT=8501
```

### Model Selection

Edit `config.py` to customize:

```python
# Primary MedGemma model
MEDGEMMA_MODEL_NAME = "google/medgemma-4b-it"

# Foundation models
CXR_FOUNDATION_MODEL = "google/cxr-foundation"
DERM_FOUNDATION_MODEL = "google/derm-foundation"
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Inference latency | ~2.3s (GPU) |
| RAG retrieval | <50ms |
| Memory usage | 4-8 GB |
| Offline capable | ✅ Yes |

Run benchmarks:
```bash
python scripts/benchmark.py --quick
```

## 🌍 Impact

### Target Users
- **5+ million** Community Health Workers globally
- Focus: Sub-Saharan Africa, South Asia

### Projected Outcomes
- **65%** faster consultations
- **72%** reduction in missed serious cases
- **$207M** annual savings from optimized referrals

See [IMPACT_STORY.md](docs/IMPACT_STORY.md) for detailed impact analysis.

## 🛡️ Safety & Ethics

- ✅ **Triage only** - Never provides diagnoses
- ✅ **Professional referral** - Always recommends consultation
- ✅ **Source citation** - Transparent about guidelines used
- ✅ **Emergency detection** - Flags critical symptoms
- ✅ **Privacy-first** - All data stays local

## 📄 Competition Deliverables

| Document | Description |
|----------|-------------|
| [COMPETITION_WRITEUP.md](docs/COMPETITION_WRITEUP.md) | 3-page submission |
| [IMPACT_STORY.md](docs/IMPACT_STORY.md) | User journey & metrics |
| [PERFORMANCE_ANALYSIS.md](docs/PERFORMANCE_ANALYSIS.md) | Benchmarks |
| [DEPLOYMENT_CHALLENGES.md](docs/DEPLOYMENT_CHALLENGES.md) | Deployment guide |
| [fine_tuning_guide.py](notebooks/fine_tuning_guide.py) | Fine-tuning tutorial |

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

## 🤝 Contributing

Contributions welcome! See our documentation for guidelines.

## ⚠️ Disclaimer

**Keneya Lens is a support tool for healthcare workers, not a replacement for professional medical judgment. Always consult qualified healthcare professionals for definitive diagnosis and treatment decisions.**

---

Built with ❤️ for Community Health Workers worldwide

*MedGemma Impact Challenge 2026*
