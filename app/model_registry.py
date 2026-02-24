"""
HAI-DEF Model Registry: Multi-model management for Health AI Developer Foundations

This module provides a unified interface for managing multiple HAI-DEF models:
- MedGemma (text and multimodal)
- CXR Foundation (chest X-ray)
- Derm Foundation (dermatology)
- Path Foundation (pathology)
"""

import os
import logging
from typing import Dict, Optional, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass

import torch

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported HAI-DEF model types."""
    MEDGEMMA_TEXT = "medgemma_text"
    MEDGEMMA_MULTIMODAL = "medgemma_multimodal"
    CXR_FOUNDATION = "cxr_foundation"
    DERM_FOUNDATION = "derm_foundation"
    PATH_FOUNDATION = "path_foundation"


class QueryType(Enum):
    """Types of medical queries for automatic model routing."""
    SYMPTOM_TRIAGE = "symptom_triage"
    CHEST_XRAY = "chest_xray"
    SKIN_LESION = "skin_lesion"
    PATHOLOGY = "pathology"
    GENERAL_MEDICAL = "general_medical"
    MULTIMODAL = "multimodal"


@dataclass
class ModelInfo:
    """Information about a HAI-DEF model."""
    model_id: str
    model_type: ModelType
    description: str
    is_multimodal: bool
    min_memory_gb: float
    supported_query_types: List[QueryType]
    huggingface_url: str


# HAI-DEF Model Registry
HAIDEF_MODELS: Dict[ModelType, ModelInfo] = {
    ModelType.MEDGEMMA_TEXT: ModelInfo(
        model_id="google/medgemma-4b-it",
        model_type=ModelType.MEDGEMMA_TEXT,
        description="MedGemma 4B instruction-tuned for medical text understanding",
        is_multimodal=False,
        min_memory_gb=8.0,
        supported_query_types=[QueryType.SYMPTOM_TRIAGE, QueryType.GENERAL_MEDICAL],
        huggingface_url="https://huggingface.co/google/medgemma-4b-it"
    ),
    ModelType.MEDGEMMA_MULTIMODAL: ModelInfo(
        model_id="google/medgemma-4b-it",
        model_type=ModelType.MEDGEMMA_MULTIMODAL,
        description="MedGemma 4B with multimodal capabilities for image+text",
        is_multimodal=True,
        min_memory_gb=10.0,
        supported_query_types=[QueryType.MULTIMODAL, QueryType.GENERAL_MEDICAL],
        huggingface_url="https://huggingface.co/google/medgemma-4b-it"
    ),
    ModelType.CXR_FOUNDATION: ModelInfo(
        model_id="google/cxr-foundation",
        model_type=ModelType.CXR_FOUNDATION,
        description="Chest X-ray Foundation model for radiograph analysis",
        is_multimodal=True,
        min_memory_gb=4.0,
        supported_query_types=[QueryType.CHEST_XRAY],
        huggingface_url="https://huggingface.co/google/cxr-foundation"
    ),
    ModelType.DERM_FOUNDATION: ModelInfo(
        model_id="google/derm-foundation",
        model_type=ModelType.DERM_FOUNDATION,
        description="Dermatology Foundation model for skin condition analysis",
        is_multimodal=True,
        min_memory_gb=4.0,
        supported_query_types=[QueryType.SKIN_LESION],
        huggingface_url="https://huggingface.co/google/derm-foundation"
    ),
    ModelType.PATH_FOUNDATION: ModelInfo(
        model_id="google/path-foundation",
        model_type=ModelType.PATH_FOUNDATION,
        description="Pathology Foundation model for histopathology image analysis",
        is_multimodal=True,
        min_memory_gb=4.0,
        supported_query_types=[QueryType.PATHOLOGY],
        huggingface_url="https://huggingface.co/google/path-foundation"
    ),
}


class QueryRouter:
    """
    Intelligent routing of medical queries to appropriate HAI-DEF models.

    Uses keyword matching and image type detection to select the best model
    for each query type.
    """

    # Keywords for query type detection
    CHEST_XRAY_KEYWORDS = [
        "chest x-ray", "chest xray", "cxr", "lung", "thorax", "thoracic",
        "pneumonia", "tuberculosis", "tb", "pulmonary", "pleural",
        "cardiomegaly", "effusion", "infiltrate", "opacity", "nodule"
    ]

    SKIN_KEYWORDS = [
        "skin", "rash", "lesion", "mole", "melanoma", "dermatitis",
        "eczema", "psoriasis", "acne", "wound", "burn", "ulcer",
        "blister", "hives", "itching", "bump", "spot", "discoloration"
    ]

    PATHOLOGY_KEYWORDS = [
        "pathology", "histology", "biopsy", "microscopy", "tissue",
        "cell", "cytology", "specimen", "slide", "stain", "tumor",
        "malignant", "benign", "carcinoma", "adenoma"
    ]

    @classmethod
    def detect_query_type(
        cls,
        query: str,
        has_image: bool = False,
        image_type: Optional[str] = None
    ) -> QueryType:
        """
        Detect the type of medical query for model routing.

        Args:
            query: The user's query text
            has_image: Whether an image is included
            image_type: Type of image if provided (xray, skin, pathology, etc.)

        Returns:
            QueryType for routing to appropriate model
        """
        query_lower = query.lower()

        # Check for explicit image type
        if image_type:
            image_type_lower = image_type.lower()
            if any(kw in image_type_lower for kw in ["xray", "x-ray", "chest", "cxr"]):
                return QueryType.CHEST_XRAY
            elif any(kw in image_type_lower for kw in ["skin", "derm", "lesion"]):
                return QueryType.SKIN_LESION
            elif any(kw in image_type_lower for kw in ["path", "histo", "biopsy"]):
                return QueryType.PATHOLOGY

        # Check keywords in query
        if any(kw in query_lower for kw in cls.CHEST_XRAY_KEYWORDS):
            return QueryType.CHEST_XRAY

        if any(kw in query_lower for kw in cls.SKIN_KEYWORDS):
            return QueryType.SKIN_LESION

        if any(kw in query_lower for kw in cls.PATHOLOGY_KEYWORDS):
            return QueryType.PATHOLOGY

        # Default based on image presence
        if has_image:
            return QueryType.MULTIMODAL

        return QueryType.SYMPTOM_TRIAGE

    @classmethod
    def get_model_for_query(
        cls,
        query: str,
        has_image: bool = False,
        image_type: Optional[str] = None,
        available_models: Optional[List[ModelType]] = None
    ) -> Tuple[ModelType, QueryType]:
        """
        Get the best model for a given query.

        Args:
            query: The user's query text
            has_image: Whether an image is included
            image_type: Type of image if provided
            available_models: List of available loaded models

        Returns:
            Tuple of (ModelType, QueryType) for the best match
        """
        query_type = cls.detect_query_type(query, has_image, image_type)

        # Model priority for each query type
        model_priority = {
            QueryType.SYMPTOM_TRIAGE: [ModelType.MEDGEMMA_TEXT],
            QueryType.CHEST_XRAY: [ModelType.CXR_FOUNDATION, ModelType.MEDGEMMA_MULTIMODAL],
            QueryType.SKIN_LESION: [ModelType.DERM_FOUNDATION, ModelType.MEDGEMMA_MULTIMODAL],
            QueryType.PATHOLOGY: [ModelType.PATH_FOUNDATION, ModelType.MEDGEMMA_MULTIMODAL],
            QueryType.GENERAL_MEDICAL: [ModelType.MEDGEMMA_TEXT],
            QueryType.MULTIMODAL: [ModelType.MEDGEMMA_MULTIMODAL, ModelType.MEDGEMMA_TEXT],
        }

        # Find best available model
        priority_list = model_priority.get(query_type, [ModelType.MEDGEMMA_TEXT])

        if available_models:
            for model_type in priority_list:
                if model_type in available_models:
                    return model_type, query_type
            # Fallback to first available
            return available_models[0], query_type

        # Return ideal model if no availability constraint
        return priority_list[0], query_type


class HAIDEFModelManager:
    """
    Manager for loading and caching multiple HAI-DEF models.

    Supports lazy loading and memory management for running multiple
    models efficiently on resource-constrained devices.
    """

    def __init__(
        self,
        default_device: str = "auto",
        max_loaded_models: int = 2,
        enable_quantization: bool = True
    ):
        """
        Initialize the HAI-DEF model manager.

        Args:
            default_device: Device for model loading ("auto", "cpu", "cuda")
            max_loaded_models: Maximum models to keep in memory
            enable_quantization: Whether to use 8-bit quantization
        """
        self.default_device = default_device
        self.max_loaded_models = max_loaded_models
        self.enable_quantization = enable_quantization

        self._loaded_models: Dict[ModelType, Any] = {}
        self._loaded_tokenizers: Dict[ModelType, Any] = {}
        self._load_order: List[ModelType] = []

        self.router = QueryRouter()

        logger.info(f"HAI-DEF Model Manager initialized (max_models={max_loaded_models})")

    def get_available_models(self) -> List[ModelType]:
        """Get list of currently loaded models."""
        return list(self._loaded_models.keys())

    def is_model_loaded(self, model_type: ModelType) -> bool:
        """Check if a model is currently loaded."""
        return model_type in self._loaded_models

    def _evict_oldest_model(self):
        """Evict the least recently used model to free memory."""
        if self._load_order:
            oldest = self._load_order.pop(0)
            logger.info(f"Evicting model {oldest.value} to free memory")

            if oldest in self._loaded_models:
                del self._loaded_models[oldest]
            if oldest in self._loaded_tokenizers:
                del self._loaded_tokenizers[oldest]

            # Force garbage collection
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def load_model(
        self,
        model_type: ModelType,
        force_reload: bool = False
    ) -> Tuple[Any, Any]:
        """
        Load a HAI-DEF model and its tokenizer.

        Args:
            model_type: Type of model to load
            force_reload: Force reload even if already loaded

        Returns:
            Tuple of (model, tokenizer)
        """
        if model_type in self._loaded_models and not force_reload:
            # Move to end of load order (most recently used)
            if model_type in self._load_order:
                self._load_order.remove(model_type)
            self._load_order.append(model_type)
            return self._loaded_models[model_type], self._loaded_tokenizers[model_type]

        # Evict if necessary
        while len(self._loaded_models) >= self.max_loaded_models:
            self._evict_oldest_model()

        model_info = HAIDEF_MODELS[model_type]
        logger.info(f"Loading {model_type.value}: {model_info.model_id}")

        # Import here to avoid circular imports
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        hf_token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")

        # Load tokenizer
        tokenizer_kwargs = {"trust_remote_code": True}
        if hf_token:
            tokenizer_kwargs["token"] = hf_token

        tokenizer = AutoTokenizer.from_pretrained(
            model_info.model_id,
            **tokenizer_kwargs
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Prepare model kwargs
        model_kwargs = {"trust_remote_code": True}
        if hf_token:
            model_kwargs["token"] = hf_token

        # Determine device and quantization
        if torch.cuda.is_available() and self.default_device != "cpu":
            if self.enable_quantization:
                try:
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        llm_int8_threshold=6.0
                    )
                    model_kwargs.update({
                        "device_map": "auto",
                        "quantization_config": quantization_config,
                        "torch_dtype": torch.float16
                    })
                except Exception as e:
                    logger.warning(f"Quantization failed: {e}")
                    model_kwargs.update({
                        "device_map": "auto",
                        "torch_dtype": torch.float16
                    })
            else:
                model_kwargs.update({
                    "device_map": "auto",
                    "torch_dtype": torch.float16
                })
        else:
            model_kwargs.update({
                "device_map": "cpu",
                "torch_dtype": torch.float32
            })

        model = AutoModelForCausalLM.from_pretrained(
            model_info.model_id,
            **model_kwargs
        )
        model.eval()

        # Cache model and tokenizer
        self._loaded_models[model_type] = model
        self._loaded_tokenizers[model_type] = tokenizer
        self._load_order.append(model_type)

        logger.info(f"Successfully loaded {model_type.value}")
        return model, tokenizer

    def route_and_load(
        self,
        query: str,
        has_image: bool = False,
        image_type: Optional[str] = None
    ) -> Tuple[Any, Any, ModelType, QueryType]:
        """
        Route query to appropriate model and load it if needed.

        Args:
            query: The user's query
            has_image: Whether an image is included
            image_type: Type of image if provided

        Returns:
            Tuple of (model, tokenizer, model_type, query_type)
        """
        model_type, query_type = self.router.get_model_for_query(
            query, has_image, image_type, self.get_available_models()
        )

        model, tokenizer = self.load_model(model_type)
        return model, tokenizer, model_type, query_type

    def get_model_info(self, model_type: ModelType) -> ModelInfo:
        """Get information about a model."""
        return HAIDEF_MODELS[model_type]

    def get_all_model_info(self) -> Dict[ModelType, ModelInfo]:
        """Get information about all available models."""
        return HAIDEF_MODELS.copy()

    def cleanup(self):
        """Unload all models and free memory."""
        logger.info("Cleaning up all loaded models")
        self._loaded_models.clear()
        self._loaded_tokenizers.clear()
        self._load_order.clear()

        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Singleton instance
_model_manager: Optional[HAIDEFModelManager] = None


def get_model_manager(
    default_device: str = "auto",
    max_loaded_models: int = 2,
    enable_quantization: bool = True
) -> HAIDEFModelManager:
    """
    Get or create the singleton HAI-DEF model manager.

    Args:
        default_device: Device for model loading
        max_loaded_models: Maximum models to keep in memory
        enable_quantization: Whether to use 8-bit quantization

    Returns:
        HAIDEFModelManager instance
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = HAIDEFModelManager(
            default_device=default_device,
            max_loaded_models=max_loaded_models,
            enable_quantization=enable_quantization
        )
    return _model_manager
