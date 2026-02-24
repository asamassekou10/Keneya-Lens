# MedLens - Complete Local Setup Guide

## 🎯 Quick Start (5 Minutes)

### Prerequisites Check
- Python 3.8+ installed
- 8GB+ RAM available
- 10GB+ free disk space (for models)
- Internet connection (first run only, for model download)

### Step-by-Step Setup

#### 1. Clone/Navigate to Project
```bash
cd "D:\Keneya Lens"  # or your project path
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation
```bash
python test_engine.py
```

#### 5. Start the Backend (Terminal 1)
```bash
python run_api.py
# Or: uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

#### 6. Start the Frontend (Terminal 2)
```bash
python run_streamlit.py
# Or: streamlit run app/streamlit_app.py
```

#### 7. Open Browser
Navigate to: `http://localhost:8501`

## 📋 Detailed Setup Instructions

### Windows Setup

#### Option A: Using PowerShell (Recommended)
```powershell
# Navigate to project
cd "D:\Keneya Lens"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If activation fails, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Start backend
python run_api.py

# In new terminal, start frontend
python run_streamlit.py
```

#### Option B: Using Command Prompt
```cmd
cd "D:\Keneya Lens"
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python run_api.py
```

### Linux/Mac Setup

```bash
# Navigate to project
cd ~/path/to/MedLens

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
python run_api.py

# In new terminal, start frontend
python run_streamlit.py
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` to customize:
```env
# Model Configuration
MEDGEMMA_MODEL=google/gemma-2-2b-it
DEVICE=auto  # or "cpu" or "cuda"

# API Configuration
API_PORT=8000
STREAMLIT_PORT=8501

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Using Configuration File

Edit `config.py` directly if you prefer:
```python
MEDGEMMA_MODEL_NAME = "google/gemma-2-2b-it"
DEVICE = "auto"  # or "cpu" or "cuda"
```

## 🚀 Usage Scenarios

### Scenario 1: First-Time User

1. **Start Backend**
   ```bash
   python run_api.py
   ```
   Wait for: "Application startup complete" and "Uvicorn running on..."

2. **Start Frontend** (new terminal)
   ```bash
   python run_streamlit.py
   ```

3. **First Query**
   - The model will download automatically (~4GB, one-time)
   - This may take 5-15 minutes depending on internet speed
   - Progress shown in backend terminal

4. **Upload Medical Guidelines** (Optional but Recommended)
   - Use sidebar "Upload Medical Guidelines"
   - Upload a PDF with medical protocols
   - Wait for "Successfully ingested" message

5. **Query Symptoms**
   - Enter symptoms in main text area
   - Click "Analyze Symptoms"
   - Review response and sources

### Scenario 2: Using with Medical Images

1. **Navigate to Image Analysis Tab**
2. **Upload Image**
   - Supported: JPEG, PNG
   - Max size: 10MB
   - Recommended: 224x224 to 1024x1024 pixels
3. **Select Image Type**
   - Skin lesion
   - X-ray
   - Ultrasound
   - Other
4. **Click "Analyze Image"**
5. **Review Analysis**

### Scenario 3: Reviewing Query History

1. **Navigate to Query History Tab**
2. **View Recent Queries**
   - See all past queries with timestamps
   - Expand to see full details
3. **Check Statistics**
   - Total queries
   - Average context chunks used

## 🐛 Troubleshooting

### Problem: Backend Won't Start

**Error**: `Address already in use`
```bash
# Windows: Find process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac: Find and kill process
lsof -ti:8000 | xargs kill -9
```

**Error**: `ModuleNotFoundError`
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Error**: `CUDA out of memory`
```bash
# Force CPU mode
# Edit config.py or set environment variable:
export DEVICE=cpu
# Or edit config.py: DEVICE = "cpu"
```

### Problem: Model Download Fails

**Solution 1**: Check internet connection
```bash
# Test HuggingFace connection
curl https://huggingface.co
```

**Solution 2**: Use HuggingFace token (for private models)
```bash
# Set token in environment
export HUGGINGFACE_TOKEN=your_token_here
```

**Solution 3**: Manual model download
```bash
# Download model manually
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('google/gemma-2-2b-it')"
```

### Problem: Streamlit Can't Connect to API

**Check**:
1. Backend is running on port 8000
2. No firewall blocking connection
3. API_BASE_URL in streamlit_app.py matches backend

**Fix**:
```python
# Edit app/streamlit_app.py line 23
API_BASE_URL = "http://localhost:8000"  # Make sure this matches
```

### Problem: PDF Ingestion Fails

**Error**: `No chunks extracted from PDF`
- PDF might be image-based (scanned)
- Try OCR-enabled PDF processor
- Check PDF is not corrupted

**Error**: `File too large`
- Maximum PDF size: 50MB
- Split large PDFs into smaller files

### Problem: Out of Memory

**Solutions**:
1. Use CPU mode (slower but less memory)
2. Reduce chunk size in PDF processing
3. Close other applications
4. Use smaller embedding model

```python
# Edit app/medgemma_engine.py
embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"  # Already small
```

## 📊 Performance Tips

### For Faster Inference

1. **Use GPU** (if available)
   ```python
   DEVICE = "cuda"  # in config.py
   ```

2. **Reduce Max Tokens**
   - Lower max_tokens = faster generation
   - Default: 512, try 256 for faster responses

3. **Lower Temperature**
   - temperature=0.3 for faster, more deterministic responses

### For Lower Memory Usage

1. **Use CPU Mode**
   ```python
   DEVICE = "cpu"
   ```

2. **Enable 8-bit Quantization** (automatic on GPU)
   - Already enabled in code

3. **Reduce Chunk Size**
   ```python
   chunk_size=300  # instead of 500
   ```

## 🔍 Verification Checklist

After setup, verify everything works:

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Health check returns "healthy"
- [ ] Can make a test query
- [ ] Can upload a PDF
- [ ] Can analyze an image
- [ ] Query history is saved
- [ ] Statistics are tracked

### Quick Verification Script

```bash
# Test backend health
curl http://localhost:8000/health

# Test query (requires backend running)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "Fever and headache for 2 days"}'
```

## 📚 Example Workflows

### Workflow 1: Setting Up for First Use

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Start backend
python run_api.py &
# Wait for "Application startup complete"

# 3. Start frontend
python run_streamlit.py

# 4. Open browser to http://localhost:8501
# 5. Upload medical guidelines PDF
# 6. Make first query (model downloads automatically)
```

### Workflow 2: Daily Usage

```bash
# Terminal 1: Start backend
python run_api.py

# Terminal 2: Start frontend  
python run_streamlit.py

# Use browser at http://localhost:8501
# - Query symptoms
# - Analyze images
# - Review history
```

### Workflow 3: Batch Processing

```python
# Use API directly for batch processing
import requests

API_URL = "http://localhost:8000"

symptoms_list = [
    "Fever and headache",
    "Cough and chest pain",
    "Skin rash and itching"
]

for symptoms in symptoms_list:
    response = requests.post(
        f"{API_URL}/query",
        json={"symptoms": symptoms}
    )
    print(response.json()["response"])
```

## 🎓 Learning Resources

### Understanding the Components

1. **MedGemma Engine** (`app/medgemma_engine.py`)
   - Loads the language model
   - Manages vector database
   - Performs RAG queries

2. **FastAPI Backend** (`app/api.py`)
   - REST API endpoints
   - Request validation
   - Rate limiting

3. **Streamlit Frontend** (`app/streamlit_app.py`)
   - User interface
   - Connects to backend API
   - Displays results

### Customization Examples

**Change Model**:
```python
# In app/medgemma_engine.py or config.py
model_name = "your-model-name"
```

**Change Ports**:
```python
# Backend: Edit run_api.py
uvicorn.run(..., port=8001)

# Frontend: Edit run_streamlit.py
streamlit run ... --server.port=8502
```

**Add Custom Prompt**:
```python
# In app/medgemma_engine.py
SYSTEM_PROMPT = """Your custom prompt here..."""
```

## 💡 Pro Tips

1. **Keep Backend Running**: Start backend once, keep it running
2. **Use Query History**: Review past queries to improve future ones
3. **Upload Guidelines**: Better RAG results with relevant medical guidelines
4. **Monitor Logs**: Check backend terminal for errors
5. **Save Responses**: Use query history to save important responses

## 🆘 Getting Help

If you encounter issues:

1. Check `TROUBLESHOOTING.md` (if exists)
2. Review backend logs for errors
3. Check query history for patterns
4. Verify all dependencies installed
5. Test with simple queries first

## ✅ Success Indicators

You'll know everything is working when:

- ✅ Backend shows "Application startup complete"
- ✅ Frontend shows "API Connected" in sidebar
- ✅ Health check returns status: "healthy"
- ✅ Test query returns a response
- ✅ Query appears in history
- ✅ Statistics show query count

---

**Ready to use!** Start with a simple symptom query and explore the features.
