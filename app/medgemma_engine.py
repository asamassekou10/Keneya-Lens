"""
MedGemma Engine: Core class for loading HAI-DEF models and performing RAG-based queries

This engine supports:
- MedGemma (text and multimodal) for medical reasoning
- CXR Foundation for chest X-ray analysis
- Derm Foundation for skin lesion analysis
- Path Foundation for pathology image analysis

Part of Keneya Lens - Offline-First Medical AI for Community Health Workers
Built for the MedGemma Impact Challenge 2026
"""
import os
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path
import logging

# Compatibility check before importing heavy dependencies
try:
    import torch
    # Check PyTorch version
    torch_version = torch.__version__
    major, minor = map(int, torch_version.split('.')[:2])
    if major < 2 or (major == 2 and minor < 1):
        raise ImportError(
            f"PyTorch {torch_version} is too old. "
            "Please upgrade: pip install --upgrade torch>=2.1.0"
        )
except ImportError as e:
    raise ImportError(
        "PyTorch not installed or incompatible. "
        "Run: pip install torch>=2.1.0 or python scripts/fix_dependencies.py"
    ) from e

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
except AttributeError as e:
    if 'register_pytree_node' in str(e):
        raise ImportError(
            "PyTorch/transformers compatibility error. "
            "Run: python scripts/fix_dependencies.py"
        ) from e
    raise

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Import HAI-DEF model components
from .model_registry import (
    ModelType, QueryType, QueryRouter,
    HAIDEFModelManager, get_model_manager, HAIDEF_MODELS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedGemmaEngine:
    """
    Main engine for HAI-DEF models with RAG capabilities.

    Supports multiple HAI-DEF models:
    - MedGemma for text-based medical reasoning
    - CXR Foundation for chest X-ray analysis
    - Derm Foundation for skin lesion analysis
    - Path Foundation for pathology image analysis

    Features:
    - Automatic query routing to appropriate models
    - RAG-augmented responses from medical guidelines
    - Offline-first operation
    - Memory-efficient model management
    """

    # System prompt for safe, ethical medical responses
    SYSTEM_PROMPT = """You are MedLens (Keneya Lens), an AI medical assistant designed to help Community Health Workers with symptom triage and medical guidance.

CRITICAL SAFETY GUIDELINES:
1. You are a SUPPORT TOOL, not a replacement for professional medical judgment
2. Always recommend consulting qualified healthcare professionals for definitive diagnosis
3. Never provide definitive diagnoses - only triage recommendations and educational information
4. If symptoms suggest a medical emergency, clearly state this and recommend immediate medical attention
5. Always cite your sources when referencing medical guidelines or protocols
6. Be transparent about limitations and uncertainties
7. Respect patient privacy and confidentiality
8. Consider resource constraints in rural settings when making recommendations

RESPONSE FORMAT:
- Provide a clear, plain-language explanation of the symptoms
- Offer evidence-based triage recommendations (e.g., "Seek immediate care", "Schedule appointment", "Monitor at home")
- Cite relevant medical guidelines or protocols when available
- Include relevant context from similar cases if available
- End with a reminder to consult healthcare professionals for definitive care

Remember: Your role is to support, not replace, professional medical judgment."""

    def __init__(
        self,
        model_name: str = "google/gemma-2-2b-it",
        medgemma_model_name: Optional[str] = None,
        device: str = "auto",
        db_path: str = "./data/chroma_db",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize the MedGemma Engine.
        
        Args:
            model_name: HuggingFace model identifier (default: gemma-2-2b-it as MedGemma base)
            medgemma_model_name: Specific MedGemma model if different from model_name
            device: Device to run model on ("auto", "cpu", "cuda")
            db_path: Path to ChromaDB storage
            embedding_model_name: Sentence transformer model for embeddings
        """
        self.device = device
        self.db_path = db_path
        self.model_name = medgemma_model_name or model_name
        
        logger.info(f"Initializing MedGemma Engine with model: {self.model_name}")
        
        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Initialize ChromaDB
        self._init_vector_db()
        
        # Initialize LLM model
        self._load_model()
        
        logger.info("MedGemma Engine initialized successfully")
    
    def _init_vector_db(self):
        """Initialize ChromaDB vector database."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.db_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="medical_guidelines",
                metadata={"description": "Medical guidelines and reference cases"}
            )
            
            logger.info(f"Vector database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            raise
    
    def _get_available_memory_gb(self) -> float:
        """Check available system memory in GB."""
        try:
            import psutil
            return psutil.virtual_memory().available / (1024 ** 3)
        except ImportError:
            return 8.0

    def _load_model(self):
        """Load the MedGemma model and tokenizer with memory-aware strategy."""
        try:
            # Check for HuggingFace token for gated models
            hf_token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")

            # Login if token provided
            if hf_token:
                try:
                    from huggingface_hub import login
                    login(token=hf_token)
                    logger.info("Authenticated with HuggingFace")
                except ImportError:
                    logger.warning("huggingface_hub not installed.")
                except Exception as e:
                    logger.warning(f"HuggingFace authentication failed: {e}")
            else:
                logger.info("No HUGGINGFACE_TOKEN found. If model is gated, authentication may be required.")

            # Check available memory
            available_gb = self._get_available_memory_gb()
            logger.info(f"Available RAM: {available_gb:.1f} GB")

            if available_gb < 4.0:
                logger.warning(
                    f"LOW MEMORY: Only {available_gb:.1f} GB available. "
                    f"Close other applications to free at least 6 GB for model loading."
                )

            logger.info(f"Loading tokenizer for {self.model_name}...")
            tokenizer_kwargs = {"trust_remote_code": True}
            if hf_token:
                tokenizer_kwargs["token"] = hf_token

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                **tokenizer_kwargs
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.info(f"Loading model {self.model_name} (this may take several minutes)...")

            model_kwargs = {
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            if hf_token:
                model_kwargs["token"] = hf_token

            if torch.cuda.is_available() and self.device != "cpu":
                # GPU mode with quantization
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
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name, **model_kwargs
                    )
                except Exception as e:
                    logger.warning(f"8-bit quantization failed, trying FP16: {e}")
                    model_kwargs.pop("quantization_config", None)
                    model_kwargs.update({
                        "device_map": "auto",
                        "torch_dtype": torch.float16
                    })
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name, **model_kwargs
                    )
            else:
                # CPU mode - use float16 to halve memory usage
                model_kwargs.update({
                    "device_map": "cpu",
                    "torch_dtype": torch.float16,
                })
                try:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name, **model_kwargs
                    )
                except (OSError, RuntimeError) as e:
                    error_str = str(e).lower()
                    if "paging" in error_str or "memory" in error_str or "1455" in error_str:
                        avail = self._get_available_memory_gb()
                        raise MemoryError(
                            f"Insufficient memory to load {self.model_name}. "
                            f"Available RAM: {avail:.1f} GB. "
                            f"Close other applications to free at least 6 GB and try again."
                        ) from e
                    raise

            self.model.eval()
            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def ingest_medical_guidelines(self, pdf_path: str, chunk_size: int = 500, overlap: int = 50):
        """
        Ingest medical guidelines from a PDF file into the vector database.
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Size of text chunks
            overlap: Overlap between chunks
        """
        try:
            from utils.pdf_processor import process_medical_pdf
            
            logger.info(f"Processing PDF: {pdf_path}")
            chunks = process_medical_pdf(pdf_path, chunk_size, overlap)
            
            if not chunks:
                logger.warning("No chunks extracted from PDF")
                return
            
            # Generate embeddings
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            
            # Prepare documents for ChromaDB
            ids = [f"{chunk['source']}_chunk_{chunk['chunk_id']}" for chunk in chunks]
            metadatas = [
                {
                    'source': chunk['source'],
                    'chunk_id': chunk['chunk_id'],
                    'total_chunks': chunk['total_chunks']
                }
                for chunk in chunks
            ]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully ingested {len(chunks)} chunks from {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error ingesting medical guidelines: {e}")
            raise
    
    def _retrieve_relevant_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant context from vector database using RAG.
        
        Args:
            query: User query/symptoms
            top_k: Number of top results to retrieve
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Check if database has any documents
            collection_count = self.collection.count()
            if collection_count == 0:
                logger.warning("Vector database is empty. Query will proceed without RAG context.")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=min(top_k, collection_count)  # Don't request more than available
            )
            
            # Format results
            contexts = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    contexts.append({
                        'text': doc,
                        'source': results['metadatas'][0][i].get('source', 'unknown'),
                        'chunk_id': results['metadatas'][0][i].get('chunk_id', -1)
                    })
            
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def query_symptoms(self, user_input: str, max_new_tokens: int = 512, temperature: float = 0.7) -> Dict:
        """
        Query symptoms and generate triage recommendation using RAG.
        
        Args:
            user_input: User's symptom description
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary containing response, context sources, and metadata
        """
        try:
            # Retrieve relevant context
            contexts = self._retrieve_relevant_context(user_input, top_k=3)
            
            # Build context string
            context_str = ""
            sources = []
            if contexts:
                context_str = "\n\n--- Relevant Medical Guidelines ---\n"
                for ctx in contexts:
                    context_str += f"\n[Source: {ctx['source']}]\n{ctx['text']}\n"
                    sources.append(ctx['source'])
            else:
                # Add note when no context is available
                context_str = "\n\n--- Note: No specific medical guidelines found in database. Response based on general medical knowledge. ---\n"
                logger.info("No RAG context available, using model's general knowledge")
            
            # Build prompt
            prompt = f"""{self.SYSTEM_PROMPT}

--- User Query ---
{user_input}

{context_str}

--- Response ---
"""
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )
            
            # Move inputs to model device
            if hasattr(self.model, 'device'):
                inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            elif torch.cuda.is_available() and self.device != "cpu":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new generated text (remove prompt)
            if prompt in response:
                response = response.split("--- Response ---")[-1].strip()
            
            return {
                'response': response,
                'sources': list(set(sources)),
                'context_count': len(contexts),
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error querying symptoms: {e}")
            return {
                'response': f"I apologize, but I encountered an error processing your query: {str(e)}. Please consult a healthcare professional.",
                'sources': [],
                'context_count': 0,
                'model': self.model_name,
                'error': str(e)
            }

    def analyze_medical_image(
        self,
        image_path: str,
        query: str = "",
        image_type: Optional[str] = None
    ) -> Dict:
        """
        Analyze a medical image using appropriate HAI-DEF foundation model.

        Automatically routes to:
        - CXR Foundation for chest X-rays
        - Derm Foundation for skin lesions
        - Path Foundation for pathology images
        - MedGemma multimodal for general medical images

        Args:
            image_path: Path to the image file
            query: Optional query about the image
            image_type: Type of image (xray, skin, pathology) for explicit routing

        Returns:
            Dictionary with analysis results and recommendations
        """
        try:
            from .foundation_models import FoundationModelFactory

            # Determine image type from query or explicit parameter
            if image_type:
                model_type = image_type.lower()
            else:
                # Auto-detect from query keywords
                query_lower = query.lower()
                if any(kw in query_lower for kw in ["xray", "x-ray", "chest", "lung", "cxr"]):
                    model_type = "cxr"
                elif any(kw in query_lower for kw in ["skin", "rash", "lesion", "mole"]):
                    model_type = "derm"
                elif any(kw in query_lower for kw in ["pathology", "biopsy", "tissue"]):
                    model_type = "path"
                else:
                    model_type = "cxr"  # Default to CXR

            logger.info(f"Analyzing image with {model_type} foundation model")

            # Get appropriate foundation model
            foundation_model = FoundationModelFactory.get_model(model_type)

            # Analyze image
            result = foundation_model.analyze(image_path)

            # Combine with MedGemma for interpretation
            interpretation_query = f"""Based on the medical image analysis:
- Image type: {model_type}
- Findings: {', '.join(result.findings)}
- Confidence: {result.confidence:.0%}

Patient query: {query if query else 'Please provide triage recommendations based on this image.'}

Provide clinical interpretation and triage recommendations."""

            # Get MedGemma interpretation
            interpretation = self.query_symptoms(interpretation_query)

            return {
                'image_analysis': {
                    'model_used': result.model_name,
                    'predictions': result.predictions,
                    'findings': result.findings,
                    'confidence': result.confidence,
                    'metadata': result.metadata
                },
                'interpretation': interpretation['response'],
                'sources': interpretation['sources'],
                'triage_recommendation': self._extract_triage_level(interpretation['response'])
            }

        except Exception as e:
            logger.error(f"Error analyzing medical image: {e}")
            return {
                'error': str(e),
                'interpretation': "Unable to analyze image. Please consult a healthcare professional.",
                'triage_recommendation': 'REFER'
            }

    def _extract_triage_level(self, response: str) -> str:
        """Extract triage level from response text."""
        response_lower = response.lower()

        if any(kw in response_lower for kw in ["urgent", "immediate", "emergency", "🔴"]):
            return "URGENT"
        elif any(kw in response_lower for kw in ["moderate", "schedule", "soon", "🟡"]):
            return "MODERATE"
        elif any(kw in response_lower for kw in ["non-urgent", "manage locally", "home", "🟢"]):
            return "NON-URGENT"
        else:
            return "REFER"  # Default to referral when uncertain

    def get_model_info(self) -> Dict:
        """Get information about loaded models."""
        return {
            'primary_model': self.model_name,
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'device': str(self.model.device) if hasattr(self.model, 'device') else self.device,
            'vector_db_path': self.db_path,
            'vector_db_count': self.collection.count(),
            'available_foundation_models': list(HAIDEF_MODELS.keys())
        }

    def health_check(self) -> Dict:
        """Perform health check on all components."""
        status = {
            'model_loaded': self.model is not None,
            'tokenizer_loaded': self.tokenizer is not None,
            'vector_db_connected': self.collection is not None,
            'vector_db_documents': 0,
            'cuda_available': torch.cuda.is_available(),
            'memory_usage_mb': 0
        }

        try:
            status['vector_db_documents'] = self.collection.count()
        except Exception:
            pass

        try:
            import psutil
            process = psutil.Process()
            status['memory_usage_mb'] = process.memory_info().rss / (1024 ** 2)
        except Exception:
            pass

        return status


class MultiModelEngine:
    """
    Extended engine supporting multiple HAI-DEF models with intelligent routing.

    This engine manages multiple models and routes queries to the most
    appropriate model based on query content and available resources.
    """

    def __init__(
        self,
        db_path: str = "./data/chroma_db",
        device: str = "auto",
        max_loaded_models: int = 2
    ):
        """
        Initialize the multi-model engine.

        Args:
            db_path: Path to ChromaDB storage
            device: Device for model loading
            max_loaded_models: Maximum models to keep in memory
        """
        self.db_path = db_path
        self.device = device

        # Initialize model manager
        self.model_manager = get_model_manager(
            default_device=device,
            max_loaded_models=max_loaded_models
        )

        # Initialize vector database
        self._init_vector_db()

        # Initialize embedding model
        self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        logger.info("MultiModelEngine initialized")

    def _init_vector_db(self):
        """Initialize ChromaDB vector database."""
        os.makedirs(self.db_path, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="medical_guidelines",
            metadata={"description": "Medical guidelines and reference cases"}
        )

    def query(
        self,
        user_input: str,
        image_path: Optional[str] = None,
        image_type: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict:
        """
        Process a query with automatic model routing.

        Args:
            user_input: User's query text
            image_path: Optional path to medical image
            image_type: Optional image type hint
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Dictionary with response and metadata
        """
        has_image = image_path is not None

        # Route to appropriate model
        model, tokenizer, model_type, query_type = self.model_manager.route_and_load(
            user_input,
            has_image=has_image,
            image_type=image_type
        )

        logger.info(f"Query routed to {model_type.value} for {query_type.value}")

        # Retrieve relevant context
        contexts = self._retrieve_context(user_input)

        # Build prompt
        prompt = self._build_prompt(user_input, contexts, query_type)

        # Generate response
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)

        if hasattr(model, 'device'):
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract response after prompt
        if "--- Response ---" in response:
            response = response.split("--- Response ---")[-1].strip()

        return {
            'response': response,
            'model_used': model_type.value,
            'query_type': query_type.value,
            'context_count': len(contexts),
            'sources': [ctx['source'] for ctx in contexts]
        }

    def _retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant context from vector database."""
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedding_model.encode([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, self.collection.count())
        )

        contexts = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0]):
                contexts.append({
                    'text': doc,
                    'source': results['metadatas'][0][i].get('source', 'unknown')
                })

        return contexts

    def _build_prompt(
        self,
        user_input: str,
        contexts: List[Dict],
        query_type: QueryType
    ) -> str:
        """Build prompt with appropriate system instructions."""
        system_prompt = MedGemmaEngine.SYSTEM_PROMPT

        context_str = ""
        if contexts:
            context_str = "\n\n--- Relevant Medical Guidelines ---\n"
            for ctx in contexts:
                context_str += f"\n[Source: {ctx['source']}]\n{ctx['text']}\n"

        return f"""{system_prompt}

--- User Query ---
{user_input}
{context_str}

--- Response ---
"""

    def get_available_models(self) -> List[str]:
        """Get list of available HAI-DEF models."""
        return [m.value for m in HAIDEF_MODELS.keys()]

    def cleanup(self):
        """Cleanup and release resources."""
        self.model_manager.cleanup()
        logger.info("MultiModelEngine cleanup complete")
