"""
FastAPI Backend for MedLens Medical Assistant
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import logging
from pathlib import Path
import time
from collections import defaultdict

from app.medgemma_engine import MedGemmaEngine
from app.agents import ConsultationOrchestrator, IntakeResult, TriageResult, GuidelineResult
from utils.validators import sanitize_text, validate_pdf_path, validate_query_params, sanitize_filename
from utils.query_logger import QueryLogger
from utils.image_processor import validate_image, preprocess_image, analyze_image_metadata

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Minimum memory (GB) required to attempt model loading
MIN_MEMORY_GB = 4.0

# Rate limiting (simple in-memory implementation)
_rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Initialize FastAPI app
app = FastAPI(
    title="MedLens API",
    description="Offline-first medical assistant API powered by MedGemma 2B",
    version="1.0.0"
)

# CORS middleware for Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance (lazy initialization)
_engine: Optional[MedGemmaEngine] = None
_query_logger: Optional[QueryLogger] = None
_engine_loading: bool = False
_engine_error: Optional[str] = None


def _get_available_memory_gb() -> float:
    """Get available system memory in GB."""
    if HAS_PSUTIL:
        return psutil.virtual_memory().available / (1024 ** 3)
    return -1.0  # Unknown


def _get_memory_info() -> dict:
    """Get detailed memory information."""
    if not HAS_PSUTIL:
        return {"available": True, "message": "Memory info unavailable (psutil not installed)"}
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 1),
        "available_gb": round(mem.available / (1024 ** 3), 1),
        "used_percent": mem.percent,
        "sufficient": mem.available / (1024 ** 3) >= MIN_MEMORY_GB,
        "min_required_gb": MIN_MEMORY_GB,
    }


def get_engine() -> MedGemmaEngine:
    """Get or initialize the MedGemma engine."""
    global _engine, _engine_loading, _engine_error
    if _engine is None:
        if _engine_loading:
            raise HTTPException(
                status_code=503,
                detail="Model is still loading. Please wait and try again."
            )

        # Check available memory before attempting to load
        available_gb = _get_available_memory_gb()
        if available_gb >= 0 and available_gb < MIN_MEMORY_GB:
            mem_info = _get_memory_info()
            error_msg = (
                f"Insufficient memory to load model. "
                f"Available: {available_gb:.1f} GB, Required: {MIN_MEMORY_GB} GB minimum. "
                f"System RAM usage: {mem_info.get('used_percent', '?')}%. "
                f"Please close other applications to free memory."
            )
            _engine_error = error_msg
            raise HTTPException(status_code=503, detail=error_msg)

        _engine_loading = True
        _engine_error = None
        try:
            logger.info("Initializing MedGemma Engine (this may take several minutes on first run)...")
            _engine = MedGemmaEngine()
            logger.info("MedGemma Engine initialized successfully")
        except Exception as e:
            _engine_error = str(e)
            logger.error(f"Failed to initialize engine: {e}")
            raise
        finally:
            _engine_loading = False
    return _engine


def get_query_logger() -> QueryLogger:
    """Get or initialize the query logger."""
    global _query_logger
    if _query_logger is None:
        _query_logger = QueryLogger()
    return _query_logger


def check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    client_requests = _rate_limit_store[client_id]
    
    # Remove old requests outside the window
    client_requests[:] = [req_time for req_time in client_requests if now - req_time < RATE_LIMIT_WINDOW]
    
    if len(client_requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    client_requests.append(now)
    return True


def get_client_id(request: Request) -> str:
    """Get client identifier for rate limiting."""
    return request.client.host if request.client else "unknown"


# Request/Response Models
class SymptomQuery(BaseModel):
    """Request model for symptom queries."""
    symptoms: str = Field(..., min_length=10, max_length=5000, description="Symptom description")
    max_tokens: Optional[int] = Field(512, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        sanitized, error = sanitize_text(v)
        if error and 'truncated' not in error.lower():
            raise ValueError(error)
        return sanitized


class QueryResponse(BaseModel):
    """Response model for symptom queries."""
    response: str
    sources: List[str]
    context_count: int
    model: str
    error: Optional[str] = None


class IngestRequest(BaseModel):
    """Request model for ingesting medical guidelines."""
    pdf_path: str
    chunk_size: Optional[int] = 500
    overlap: Optional[int] = 50


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    db_initialized: bool
    model_loading: bool = False
    error: Optional[str] = None

    model_config = {"protected_namespaces": ()}


# Background model loading on startup
import threading


def _preload_engine():
    """Pre-load the engine in a background thread, with memory safety check."""
    global _engine_error
    try:
        available_gb = _get_available_memory_gb()
        if available_gb >= 0 and available_gb < MIN_MEMORY_GB:
            msg = (
                f"Skipping background model preload: only {available_gb:.1f} GB RAM available "
                f"(need {MIN_MEMORY_GB} GB). Close other applications and use "
                f"POST /load-model to load manually when memory is available."
            )
            logger.warning(msg)
            _engine_error = msg
            return
        get_engine()
    except Exception as e:
        logger.error(f"Background engine loading failed: {e}")


@app.on_event("startup")
async def startup_event():
    """Start model loading in background when API starts (if sufficient memory)."""
    available_gb = _get_available_memory_gb()
    logger.info(f"API starting. Available RAM: {available_gb:.1f} GB (minimum {MIN_MEMORY_GB} GB needed)")
    if available_gb >= 0 and available_gb < MIN_MEMORY_GB:
        logger.warning(
            f"Insufficient memory for background model loading. "
            f"API will start without model. Use POST /load-model to load when ready."
        )
        global _engine_error
        _engine_error = (
            f"Insufficient memory: {available_gb:.1f} GB available, "
            f"{MIN_MEMORY_GB} GB required. Close applications and use POST /load-model."
        )
        return
    logger.info("Starting background model loading...")
    thread = threading.Thread(target=_preload_engine, daemon=True)
    thread.start()


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "MedLens API - Offline Medical Assistant",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "ingest": "/ingest"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint.

    Returns basic health status without initializing the model.
    Use /health/full to check model status (may take time on first call).
    """
    # Simple health check - don't initialize engine
    global _engine, _engine_loading, _engine_error
    return HealthResponse(
        status="healthy",
        model_loaded=_engine is not None and _engine.model is not None,
        db_initialized=_engine is not None and _engine.chroma_client is not None,
        model_loading=_engine_loading,
        error=_engine_error
    )


@app.get("/health/full", response_model=HealthResponse, tags=["General"])
async def health_check_full():
    """
    Full health check that initializes the model if needed.

    WARNING: First call may take several minutes to download and load the model.
    """
    try:
        engine = get_engine()
        return HealthResponse(
            status="healthy",
            model_loaded=engine.model is not None,
            db_initialized=engine.chroma_client is not None
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            db_initialized=False
        )


@app.get("/memory", tags=["General"])
async def memory_status():
    """
    Get system memory information.

    Returns available RAM and whether it's sufficient for model loading.
    """
    info = _get_memory_info()
    info["model_loaded"] = _engine is not None
    info["model_loading"] = _engine_loading
    info["engine_error"] = _engine_error
    return info


@app.post("/load-model", tags=["General"])
async def load_model_manual():
    """
    Manually trigger model loading.

    Use this endpoint when memory has been freed and you want to load the model.
    """
    global _engine_error
    if _engine is not None:
        return {"status": "already_loaded", "message": "Model is already loaded."}

    if _engine_loading:
        return {"status": "loading", "message": "Model is currently loading. Please wait."}

    available_gb = _get_available_memory_gb()
    if available_gb >= 0 and available_gb < MIN_MEMORY_GB:
        return {
            "status": "insufficient_memory",
            "message": f"Only {available_gb:.1f} GB available. Need {MIN_MEMORY_GB} GB minimum.",
            "available_gb": round(available_gb, 1),
            "required_gb": MIN_MEMORY_GB
        }

    # Clear previous error and start loading
    _engine_error = None

    def _load_in_background():
        try:
            get_engine()
        except Exception as e:
            logger.error(f"Manual model loading failed: {e}")

    thread = threading.Thread(target=_load_in_background, daemon=True)
    thread.start()

    return {
        "status": "loading_started",
        "message": "Model loading initiated. Check /health for progress.",
        "available_gb": round(available_gb, 1)
    }


# ── Agentic consultation models ────────────────────────────────────────────────

class ConsultRequest(BaseModel):
    """Request model for full multi-agent consultation."""
    symptoms: str = Field(..., min_length=10, max_length=8000,
                          description="Free-text patient presentation")
    language: str = Field("en", description="Response language: 'en' or 'fr'")
    max_tokens: Optional[int] = Field(512, ge=64, le=1024)

    @validator("symptoms")
    def validate_symptoms(cls, v):
        sanitized, error = sanitize_text(v)
        if error and "truncated" not in error.lower():
            raise ValueError(error)
        return sanitized

    @validator("language")
    def validate_language(cls, v):
        if v not in ("en", "fr"):
            return "en"
        return v


class StageRequest(BaseModel):
    """Request for a single agent stage (used for step-by-step UI polling)."""
    stage: int = Field(..., ge=1, le=4, description="Stage number: 1=Intake, 2=Triage, 3=Guidelines, 4=Recommendations")
    context: dict = Field(default_factory=dict, description="Outputs from previous stages")
    language: str = Field("en", description="Response language: 'en' or 'fr'")


# Global orchestrator instance (lazy, shares the engine)
_orchestrator: Optional[ConsultationOrchestrator] = None


def get_orchestrator() -> ConsultationOrchestrator:
    """Get or create the ConsultationOrchestrator, reusing the shared engine."""
    global _orchestrator
    if _orchestrator is None:
        engine = get_engine()
        _orchestrator = ConsultationOrchestrator(engine)
    return _orchestrator


@app.post("/consult", tags=["Agentic"])
async def full_consultation(request: ConsultRequest, req: Request):
    """
    Run a complete 4-stage multi-agent medical consultation.

    Competition note: This endpoint implements the Agentic Workflow Prize criteria.
    The pipeline runs four specialised agents in sequence:
      Stage 1 — IntakeAgent: structures free-text into a clean patient record
      Stage 2 — TriageAgent: IMCI-informed urgency assessment
      Stage 3 — GuidelineAgent: RAG retrieval from indexed clinical guidelines
      Stage 4 — RecommendationAgent: actionable clinical management plan

    Each agent has its own focused system prompt and output schema.
    Returns complete ConsultationResult as JSON.
    """
    client_id = get_client_id(req)
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    try:
        orchestrator = get_orchestrator()
        result = orchestrator.run(request.symptoms, language=request.language)

        # Log the consultation
        logger_instance = get_query_logger()
        logger_instance.log_query(
            user_input=request.symptoms,
            response=f"[AGENTIC] Triage: {result.triage.triage_level}",
            sources=result.guidelines.citations,
            context_count=result.guidelines.context_count,
            model="medgemma-agentic-pipeline",
            metadata={"triage_level": result.triage.triage_level, "language": request.language},
        )

        return result.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Consultation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Consultation failed: {str(e)}")


@app.post("/consult/stage", tags=["Agentic"])
async def run_single_stage(request: StageRequest, req: Request):
    """
    Run a single agent stage. Called sequentially by the step-by-step UI.

    The UI calls this endpoint 4 times, once per stage, storing results in session
    state and triggering a rerun between each call to progressively reveal agent cards.

    Args:
        stage: 1 (Intake), 2 (Triage), 3 (Guidelines), 4 (Recommendations)
        context: Dict containing all prior stage outputs
        language: Response language ('en' | 'fr')
    """
    client_id = get_client_id(req)
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    try:
        orchestrator = get_orchestrator()
        result = orchestrator.run_stage(request.stage, request.context, request.language)
        return {"stage": request.stage, "result": result, "success": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Stage %d failed: %s", request.stage, e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stage {request.stage} failed: {str(e)}")


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_symptoms(query: SymptomQuery, request: Request):
    """
    Query symptoms and get triage recommendations.
    
    Args:
        query: SymptomQuery object containing symptoms and generation parameters
        request: FastAPI request object for rate limiting
        
    Returns:
        QueryResponse with AI-generated response and sources
    """
    # Rate limiting
    client_id = get_client_id(request)
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per hour."
        )
    
    try:
        engine = get_engine()
        result = engine.query_symptoms(
            user_input=query.symptoms,
            max_new_tokens=query.max_tokens,
            temperature=query.temperature
        )
        
        # Log query
        logger_instance = get_query_logger()
        logger_instance.log_query(
            user_input=query.symptoms,
            response=result['response'],
            sources=result.get('sources', []),
            context_count=result.get('context_count', 0),
            model=result.get('model', 'unknown'),
            metadata={'max_tokens': query.max_tokens, 'temperature': query.temperature}
        )
        
        return QueryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/ingest", tags=["Data"])
async def ingest_guidelines(request: IngestRequest):
    """
    Ingest medical guidelines from a PDF file.
    
    Args:
        request: IngestRequest containing PDF path and chunking parameters
        
    Returns:
        Success message with number of chunks ingested
    """
    try:
        pdf_path = Path(request.pdf_path)
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF file not found: {request.pdf_path}")
        
        engine = get_engine()
        engine.ingest_medical_guidelines(
            pdf_path=str(pdf_path),
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        
        return {
            "status": "success",
            "message": f"Successfully ingested guidelines from {request.pdf_path}",
            "pdf_path": str(pdf_path)
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/upload", tags=["Data"])
async def ingest_uploaded_file(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF file.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Success message
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file content
        content = await file.read()
        
        # Validate file size (50MB max)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (maximum 50MB)")
        
        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)
        
        # Save uploaded file
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / safe_filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate PDF path
        is_valid, error_msg = validate_pdf_path(str(file_path))
        if not is_valid:
            file_path.unlink()  # Clean up
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Ingest the file
        engine = get_engine()
        engine.ingest_medical_guidelines(str(file_path))
        
        return {
            "status": "success",
            "message": f"Successfully ingested {safe_filename}",
            "filename": safe_filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/analyze/image", tags=["Query"])
async def analyze_medical_image(file: UploadFile = File(...), image_type: str = "skin lesion", request: Request = None):
    """
    Analyze a medical image (skin lesion, X-ray, etc.).
    
    Args:
        file: Uploaded image file
        image_type: Type of medical image
        request: FastAPI request object
        
    Returns:
        Analysis results
    """
    # Rate limiting
    if request:
        client_id = get_client_id(request)
        if not check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per hour."
            )
    
    try:
        # Read image
        image_data = await file.read()
        
        # Validate image
        is_valid, error_msg = validate_image(image_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Analyze metadata
        metadata = analyze_image_metadata(image_data)
        
        # Preprocess image
        processed_image = preprocess_image(image_data)
        if not processed_image:
            raise HTTPException(status_code=400, detail="Failed to process image")
        
        # Save image to a temp path for engine analysis
        import tempfile, os as _os
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = sanitize_filename(file.filename or "image.jpg")
        image_path = upload_dir / safe_name
        with open(image_path, "wb") as _f:
            _f.write(image_data)

        engine = get_engine()
        logger.info(f"Starting image analysis for {image_type} (image saved to {image_path})...")

        # Attempt multimodal analysis; falls back to text-based if model is text-only
        result = engine.analyze_medical_image(
            image_path=str(image_path),
            query=f"Please analyse this {image_type} image and provide clinical findings.",
            image_type=image_type,
        )
        logger.info("Image analysis completed")
        
        # Log query
        logger_instance = get_query_logger()
        logger_instance.log_query(
            user_input=f"[IMAGE ANALYSIS] {image_type}",
            response=result['response'],
            sources=result.get('sources', []),
            context_count=result.get('context_count', 0),
            model=result.get('model', 'unknown'),
            metadata={'image_type': image_type, 'image_metadata': metadata}
        )
        
        # analyze_medical_image returns a nested dict; flatten for API response
        if "interpretation" in result:
            # Came from foundation model path
            response_text = result.get("interpretation", "")
            sources = result.get("sources", [])
            image_analysis = result.get("image_analysis", {})
        else:
            # Came from text-only fallback
            response_text = result.get("response", "")
            sources = result.get("sources", [])
            image_analysis = {}

        return {
            "response": response_text,
            "sources": sources,
            "image_metadata": metadata,
            "image_analysis": image_analysis,
            "image_type": image_type,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


@app.get("/history", tags=["General"])
async def get_query_history(limit: int = 10):
    """
    Get recent query history.
    
    Args:
        limit: Maximum number of queries to return
        
    Returns:
        List of recent queries
    """
    try:
        logger_instance = get_query_logger()
        queries = logger_instance.get_recent_queries(limit=min(limit, 100))
        return {"queries": queries, "count": len(queries)}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["General"])
async def get_statistics():
    """Get query statistics including knowledge base document count."""
    try:
        logger_instance = get_query_logger()
        stats = logger_instance.get_statistics()

        # Add knowledge base document count from the shared engine
        try:
            eng = _engine
            if eng is not None and eng.collection is not None:
                stats["kb_documents"] = eng.collection.count()
            else:
                stats["kb_documents"] = 0
        except Exception:
            stats["kb_documents"] = 0

        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
