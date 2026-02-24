# MedLens Troubleshooting Guide

## 🔍 Common Issues and Solutions

### Installation Issues

#### Problem: `pip install` fails
**Symptoms**: Error during dependency installation

**Solutions**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install individually if specific package fails
pip install torch transformers
```

#### Problem: `torch` installation fails
**Symptoms**: CUDA/CPU version conflicts

**Solutions**:
```bash
# CPU-only version (smaller, easier)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Or check PyTorch website for your system
# https://pytorch.org/get-started/locally/
```

### Runtime Issues

#### Problem: Backend starts but model download fails
**Symptoms**: Timeout or connection error during model download

**Solutions**:
1. **Check Internet Connection**
   ```bash
   curl https://huggingface.co
   ```

2. **Use HuggingFace Mirror** (if in restricted region)
   ```python
   # Set environment variable
   export HF_ENDPOINT=https://hf-mirror.com
   ```

3. **Manual Download**
   ```python
   from transformers import AutoModelForCausalLM
   model = AutoModelForCausalLM.from_pretrained(
       "google/gemma-2-2b-it",
       cache_dir="./models"
   )
   ```

4. **Use Local Model Path**
   ```python
   # If you have model locally
   model_name = "./models/gemma-2-2b-it"
   ```

#### Problem: Out of Memory (OOM) errors
**Symptoms**: `CUDA out of memory` or system freeze

**Solutions**:
1. **Force CPU Mode**
   ```python
   # Edit config.py
   DEVICE = "cpu"
   ```

2. **Reduce Batch Size**
   ```python
   # Already handled in code, but you can reduce chunk processing
   ```

3. **Close Other Applications**
   - Close browser tabs
   - Close other Python processes
   - Free up RAM

4. **Use Smaller Model**
   ```python
   # Edit config.py
   MEDGEMMA_MODEL_NAME = "google/gemma-2b-it"  # Smaller variant
   ```

#### Problem: Port already in use
**Symptoms**: `Address already in use` error

**Solutions**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Or change port in config
```

#### Problem: Streamlit can't connect to API
**Symptoms**: "API Disconnected" in sidebar

**Solutions**:
1. **Check Backend is Running**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API URL**
   ```python
   # Edit app/streamlit_app.py
   API_BASE_URL = "http://localhost:8000"  # Verify this
   ```

3. **Check Firewall**
   - Windows: Allow Python through firewall
   - Linux: Check iptables/ufw

4. **Try Different Port**
   ```python
   # If 8000 is blocked, use 8001
   API_BASE_URL = "http://localhost:8001"
   ```

### Model Issues

#### Problem: Model generates gibberish
**Symptoms**: Nonsensical responses

**Solutions**:
1. **Check Model Loading**
   ```python
   # Verify model loaded correctly
   print(engine.model.config)
   ```

2. **Adjust Temperature**
   ```python
   # Lower temperature for more deterministic
   temperature = 0.3  # instead of 0.7
   ```

3. **Check Prompt Format**
   - Ensure system prompt is correct
   - Verify input formatting

#### Problem: Model too slow
**Symptoms**: Very slow response times

**Solutions**:
1. **Use GPU** (if available)
   ```python
   DEVICE = "cuda"
   ```

2. **Reduce Max Tokens**
   ```python
   max_tokens = 256  # instead of 512
   ```

3. **Lower Temperature**
   ```python
   temperature = 0.3  # faster generation
   ```

4. **Check System Resources**
   ```bash
   # Monitor CPU/GPU usage
   # Close other applications
   ```

### Database Issues

#### Problem: ChromaDB errors
**Symptoms**: Database initialization fails

**Solutions**:
1. **Clear Database**
   ```bash
   rm -rf data/chroma_db/*
   # or on Windows
   rmdir /s data\chroma_db
   ```

2. **Check Permissions**
   ```bash
   # Ensure write permissions
   chmod 755 data
   ```

3. **Reinitialize**
   ```python
   # Database will recreate on next run
   ```

#### Problem: No context retrieved from RAG
**Symptoms**: Empty sources, no guidelines found

**Solutions**:
1. **Check Database Has Data**
   ```python
   # Check collection count
   print(engine.collection.count())
   ```

2. **Re-ingest PDFs**
   - Upload PDFs again
   - Check PDF has extractable text (not just images)

3. **Improve Query**
   - Use more specific medical terms
   - Include relevant keywords

### PDF Processing Issues

#### Problem: PDF ingestion fails
**Symptoms**: "No chunks extracted" or errors

**Solutions**:
1. **Check PDF Format**
   - Ensure PDF has text (not just images)
   - Try different PDF

2. **Check PDF Size**
   - Maximum: 50MB
   - Split large PDFs

3. **Try Different PDF Library**
   ```python
   # Already using pdfplumber, but you can try pypdf2
   ```

4. **OCR for Scanned PDFs**
   ```bash
   # Install OCR tools if needed
   pip install pytesseract pdf2image
   ```

### API Issues

#### Problem: Rate limit errors
**Symptoms**: HTTP 429 responses

**Solutions**:
1. **Wait for Rate Limit Reset**
   - Default: 1 hour window
   - 100 requests per hour

2. **Adjust Rate Limits**
   ```python
   # Edit app/api.py
   RATE_LIMIT_REQUESTS = 200  # Increase limit
   ```

3. **Use Different Client**
   - Rate limiting is per IP address

#### Problem: Validation errors
**Symptoms**: HTTP 400 with validation messages

**Solutions**:
1. **Check Input Format**
   - Symptoms: 10-5000 characters
   - Max tokens: 1-2048
   - Temperature: 0.0-2.0

2. **Sanitize Input**
   - Remove special characters
   - Check length limits

### Image Processing Issues

#### Problem: Image upload fails
**Symptoms**: Validation errors or processing fails

**Solutions**:
1. **Check Image Format**
   - Supported: JPEG, PNG
   - Max size: 10MB

2. **Check Image Dimensions**
   - Minimum: 64x64
   - Maximum: 4096x4096

3. **Resize Image**
   ```python
   from PIL import Image
   img = Image.open("image.jpg")
   img = img.resize((224, 224))
   img.save("resized.jpg")
   ```

## 🛠️ Debug Mode

### Enable Verbose Logging

```python
# Edit app/api.py or app/medgemma_engine.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test engine
python test_engine.py

# Test API
curl http://localhost:8000/health

# Test PDF processing
python -c "from utils.pdf_processor import process_medical_pdf; print(process_medical_pdf('test.pdf'))"
```

## 📞 Getting More Help

1. **Check Logs**
   - Backend terminal output
   - `data/logs/queries.jsonl` for query logs

2. **Run Setup Check**
   ```bash
   python scripts/setup_check.py
   ```

3. **Verify Installation**
   ```bash
   pip list | grep -E "torch|transformers|chromadb|fastapi|streamlit"
   ```

4. **Test Minimal Example**
   ```python
   from app.medgemma_engine import MedGemmaEngine
   engine = MedGemmaEngine()
   result = engine.query_symptoms("Fever")
   print(result)
   ```

## 🔧 System-Specific Issues

### Windows

**Problem**: PowerShell execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem**: Path issues
```python
# Use raw strings or forward slashes
path = r"D:\Keneya Lens\data"
```

### Linux/Mac

**Problem**: Permission denied
```bash
chmod +x scripts/*.py
```

**Problem**: Python3 vs python
```bash
# Use python3 explicitly
python3 -m venv venv
```

## ✅ Quick Health Check

Run this to verify everything:
```bash
python scripts/setup_check.py
```

Expected output:
- ✅ Python version
- ✅ Required files
- ✅ Dependencies
- ✅ Directories
- ✅ Port availability
- ✅ Disk space
