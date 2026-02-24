# MedLens Project Structure

## 📁 Complete File Tree

```
MedLens/
│
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── medgemma_engine.py       # Core MedGemma engine with RAG
│   ├── api.py                   # FastAPI backend server
│   └── streamlit_app.py         # Streamlit UI application
│
├── utils/                        # Utility functions
│   ├── __init__.py              # Package initialization
│   └── pdf_processor.py         # PDF processing and chunking
│
├── data/                         # Data storage (created at runtime)
│   ├── chroma_db/               # ChromaDB vector database
│   └── uploads/                 # Uploaded PDF files
│
├── models/                       # Model cache (auto-created by transformers)
│
├── requirements.txt              # Python dependencies
├── config.py                    # Configuration settings
├── README.md                     # Main documentation
├── QUICKSTART.md                # Quick start guide
├── PROJECT_STRUCTURE.md         # This file
├── .gitignore                   # Git ignore rules
│
├── run_api.py                   # Convenience script to run FastAPI
├── run_streamlit.py             # Convenience script to run Streamlit
└── test_engine.py               # Test script for engine verification
```

## 🔑 Key Files Explained

### Core Application Files

1. **`app/medgemma_engine.py`**
   - `MedGemmaEngine` class: Main engine for model loading and RAG
   - System prompt for safe medical responses
   - Model initialization with device mapping
   - Vector database management (ChromaDB)
   - `ingest_medical_guidelines()`: PDF ingestion and vectorization
   - `query_symptoms()`: RAG-based symptom querying

2. **`app/api.py`**
   - FastAPI backend with REST endpoints
   - `/health`: Health check
   - `/query`: Symptom query endpoint
   - `/ingest`: PDF ingestion endpoint
   - `/ingest/upload`: File upload endpoint

3. **`app/streamlit_app.py`**
   - Streamlit UI for user interaction
   - Symptom input interface
   - PDF upload functionality
   - Response display with source citations

### Utility Files

4. **`utils/pdf_processor.py`**
   - `extract_text_from_pdf()`: PDF text extraction
   - `chunk_text()`: Text chunking with overlap
   - `process_medical_pdf()`: Complete PDF processing pipeline

### Configuration & Setup

5. **`config.py`**
   - Centralized configuration
   - Environment variable support
   - Path management

6. **`requirements.txt`**
   - All Python dependencies
   - Version specifications

### Convenience Scripts

7. **`run_api.py`**: Start FastAPI backend
8. **`run_streamlit.py`**: Start Streamlit UI
9. **`test_engine.py`**: Test engine functionality

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │  (Frontend)
│  (Port 8501)    │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  FastAPI Backend │  (API Layer)
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MedGemmaEngine  │  (Core Logic)
│                 │
│  ┌───────────┐  │
│  │ MedGemma  │  │  (LLM Model)
│  │   2B      │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ ChromaDB  │  │  (Vector DB)
│  │  (RAG)    │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │Sentence   │  │  (Embeddings)
│  │Transformers│ │
│  └───────────┘  │
└─────────────────┘
```

## 🔄 Data Flow

1. **Ingestion Flow**:
   ```
   PDF → pdf_processor.py → Chunks → Embeddings → ChromaDB
   ```

2. **Query Flow**:
   ```
   User Input → Embedding → ChromaDB Search → Context Retrieval 
   → Prompt Construction → MedGemma Inference → Response
   ```

## 📦 Dependencies Overview

- **transformers**: HuggingFace model loading
- **accelerate**: Model optimization
- **torch**: PyTorch backend
- **chromadb**: Vector database
- **sentence-transformers**: Text embeddings
- **fastapi**: Backend API framework
- **streamlit**: Frontend UI framework
- **pdfplumber**: PDF text extraction

## 🚀 Getting Started

See `QUICKSTART.md` for detailed setup instructions.

## 📝 Notes

- All directories in `data/` are created automatically
- Model files are cached in `models/` by transformers
- ChromaDB persists data in `data/chroma_db/`
- Uploaded PDFs are stored in `data/uploads/`
