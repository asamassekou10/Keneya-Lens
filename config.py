"""
Configuration file for MedLens
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# =============================================================================
# HAI-DEF MODEL CONFIGURATION
# Health AI Developer Foundations (HAI-DEF) models from Google
# =============================================================================

# Primary MedGemma model for text-based medical queries
# Options: "google/medgemma-4b-it", "google/medgemma-27b-text-it"
MEDGEMMA_MODEL_NAME = os.getenv("MEDGEMMA_MODEL", "google/medgemma-4b-it")

# Multimodal MedGemma for image + text analysis
# Options: "google/medgemma-4b-it", "google/medgemma-27b-it" (multimodal)
MEDGEMMA_MULTIMODAL_MODEL = os.getenv("MEDGEMMA_MULTIMODAL_MODEL", "google/medgemma-4b-it")

# HAI-DEF Specialized Foundation Models
# CXR Foundation - Chest X-ray analysis
CXR_FOUNDATION_MODEL = os.getenv("CXR_FOUNDATION_MODEL", "google/cxr-foundation")

# Derm Foundation - Dermatology/skin lesion analysis
DERM_FOUNDATION_MODEL = os.getenv("DERM_FOUNDATION_MODEL", "google/derm-foundation")

# Path Foundation - Pathology image analysis
PATH_FOUNDATION_MODEL = os.getenv("PATH_FOUNDATION_MODEL", "google/path-foundation")

# Embedding model for RAG
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Medical embedding model (better for medical text)
MEDICAL_EMBEDDING_MODEL = os.getenv("MEDICAL_EMBEDDING_MODEL", "pritamdeka/S-PubMedBert-MS-MARCO")

# Model selection mode: "auto" (route based on query type) or "manual"
MODEL_SELECTION_MODE = os.getenv("MODEL_SELECTION_MODE", "auto")

# Device configuration
DEVICE = os.getenv("DEVICE", "auto")  # "auto", "cpu", "cuda"

# Database configuration
CHROMA_DB_PATH = str(DATA_DIR / "chroma_db")
UPLOAD_DIR = DATA_DIR / "uploads"

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Streamlit configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_ADDRESS = os.getenv("STREAMLIT_ADDRESS", "localhost")  # Use "0.0.0.0" for remote access

# Generation defaults
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))

# Chunking defaults
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "500"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "50"))

# HuggingFace Token (REQUIRED for gated models like Gemma)
# Get token from: https://huggingface.co/settings/tokens
# Request access: https://huggingface.co/google/gemma-2-2b-it
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
