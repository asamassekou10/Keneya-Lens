# Keneya Lens Application Package
# Offline-First Medical AI for Community Health Workers
# Built for the MedGemma Impact Challenge 2026

from .medgemma_engine import MedGemmaEngine, MultiModelEngine
from .model_registry import (
    ModelType,
    QueryType,
    QueryRouter,
    HAIDEFModelManager,
    get_model_manager,
    HAIDEF_MODELS
)
from .foundation_models import (
    CXRFoundationModel,
    DermFoundationModel,
    PathFoundationModel,
    FoundationModelFactory,
    ImageAnalysisResult
)

__all__ = [
    # Core engines
    "MedGemmaEngine",
    "MultiModelEngine",
    # Model registry
    "ModelType",
    "QueryType",
    "QueryRouter",
    "HAIDEFModelManager",
    "get_model_manager",
    "HAIDEF_MODELS",
    # Foundation models
    "CXRFoundationModel",
    "DermFoundationModel",
    "PathFoundationModel",
    "FoundationModelFactory",
    "ImageAnalysisResult",
]

__version__ = "2.0.0"
__author__ = "Keneya Lens Team"
__description__ = "Offline-first medical AI powered by HAI-DEF models"
