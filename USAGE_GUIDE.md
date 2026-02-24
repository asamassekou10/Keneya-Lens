# MedLens - Complete Usage Guide

## 🎯 Quick Reference

### Starting the Application

**Option 1: Automated (Easiest)**
```bash
python scripts/start_all.py
```

**Option 2: Manual (Two Terminals)**
```bash
# Terminal 1: Backend
python run_api.py

# Terminal 2: Frontend
python run_streamlit.py
```

**Option 3: Docker**
```bash
docker-compose up
```

### Access Points
- **Frontend UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📖 Detailed Usage

### 1. Initial Setup

#### Verify Installation
```bash
python scripts/setup_check.py
```

#### Create Sample Data (Optional)
```bash
python scripts/download_sample_data.py
```

### 2. Using the Web Interface

#### Symptom Query
1. Navigate to "Symptom Query" tab
2. Enter symptom description (10-5000 characters)
3. Adjust settings if needed:
   - Max Tokens: 256-1024 (default: 512)
   - Temperature: 0.0-1.0 (default: 0.7)
4. Click "Analyze Symptoms"
5. Review response and sources

#### Image Analysis
1. Navigate to "Image Analysis" tab
2. Upload image (JPEG/PNG, max 10MB)
3. Select image type (skin lesion, x-ray, etc.)
4. Click "Analyze Image"
5. Review analysis and metadata

#### Query History
1. Navigate to "Query History" tab
2. View recent queries
3. Expand entries for details
4. Check statistics dashboard

#### Upload Guidelines
1. Use sidebar "Upload Medical Guidelines"
2. Select PDF file
3. Click "Ingest PDF"
4. Wait for confirmation

### 3. Using the API

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Query Symptoms
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "Fever and headache for 2 days",
    "max_tokens": 512,
    "temperature": 0.7
  }'
```

#### Analyze Image
```bash
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@image.jpg" \
  -F "image_type=skin lesion"
```

#### Get History
```bash
curl http://localhost:8000/history?limit=10
```

#### Get Statistics
```bash
curl http://localhost:8000/stats
```

#### Upload PDF
```bash
curl -X POST http://localhost:8000/ingest/upload \
  -F "file=@guidelines.pdf"
```

### 4. Programmatic Usage

#### Python Example
```python
import requests

API_URL = "http://localhost:8000"

# Query symptoms
response = requests.post(
    f"{API_URL}/query",
    json={
        "symptoms": "Patient has fever and cough",
        "max_tokens": 512
    }
)
result = response.json()
print(result["response"])

# Upload PDF
with open("guidelines.pdf", "rb") as f:
    response = requests.post(
        f"{API_URL}/ingest/upload",
        files={"file": f}
    )
print(response.json())
```

#### Batch Processing
```python
import requests
from typing import List

API_URL = "http://localhost:8000"

symptoms_list = [
    "Fever and headache",
    "Cough and chest pain",
    "Skin rash"
]

results = []
for symptoms in symptoms_list:
    response = requests.post(
        f"{API_URL}/query",
        json={"symptoms": symptoms}
    )
    results.append(response.json())

# Process results
for result in results:
    print(f"Response: {result['response']}")
    print(f"Sources: {result['sources']}")
```

### 5. Advanced Usage

#### Custom Configuration
```python
# Edit config.py
MEDGEMMA_MODEL_NAME = "your-model"
DEVICE = "cuda"  # or "cpu"
DEFAULT_MAX_TOKENS = 256
```

#### Direct Engine Usage
```python
from app.medgemma_engine import MedGemmaEngine

# Initialize engine
engine = MedGemmaEngine(
    model_name="google/gemma-2-2b-it",
    device="auto"
)

# Ingest PDF
engine.ingest_medical_guidelines("path/to/guidelines.pdf")

# Query
result = engine.query_symptoms(
    "Fever and headache",
    max_new_tokens=512,
    temperature=0.7
)
print(result["response"])
```

#### Custom Prompt Engineering
```python
# Edit app/medgemma_engine.py
SYSTEM_PROMPT = """Your custom prompt here..."""
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Model
export MEDGEMMA_MODEL=google/gemma-2-2b-it
export DEVICE=auto

# API
export API_PORT=8000
export STREAMLIT_PORT=8501

# Rate Limiting
export RATE_LIMIT_REQUESTS=100
export RATE_LIMIT_WINDOW=3600
```

### Configuration File
Edit `config.py`:
```python
MEDGEMMA_MODEL_NAME = "google/gemma-2-2b-it"
DEVICE = "auto"
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7
```

## 📊 Best Practices

### For Better Results

1. **Upload Relevant Guidelines**
   - Use medical protocols/guidelines PDFs
   - Ensure PDFs have extractable text
   - Upload multiple relevant documents

2. **Write Detailed Queries**
   - Include symptoms, duration, severity
   - Mention relevant medical history
   - Specify patient demographics if relevant

3. **Use Appropriate Settings**
   - Lower temperature (0.3-0.5) for more focused responses
   - Higher temperature (0.7-0.9) for more creative responses
   - Adjust max_tokens based on expected response length

4. **Review Query History**
   - Learn from past queries
   - Identify patterns
   - Improve future queries

### Performance Tips

1. **Keep Backend Running**
   - Start once, reuse for multiple queries
   - Model stays loaded in memory

2. **Batch Operations**
   - Process multiple queries in sequence
   - Upload multiple PDFs at once

3. **Monitor Resources**
   - Check memory usage
   - Monitor disk space
   - Watch for rate limits

## 🎓 Example Workflows

### Workflow 1: First-Time Setup
```bash
# 1. Verify setup
python scripts/setup_check.py

# 2. Create sample data
python scripts/download_sample_data.py

# 3. Start services
python scripts/start_all.py

# 4. Open browser to http://localhost:8501
# 5. Upload sample PDF
# 6. Make test query
```

### Workflow 2: Daily Usage
```bash
# Start backend (keep running)
python run_api.py

# Start frontend when needed
python run_streamlit.py

# Use web interface for queries
```

### Workflow 3: API Integration
```python
# Integrate into your application
import requests

class MedLensClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
    
    def query(self, symptoms, max_tokens=512):
        response = requests.post(
            f"{self.api_url}/query",
            json={"symptoms": symptoms, "max_tokens": max_tokens}
        )
        return response.json()
    
    def analyze_image(self, image_path, image_type="skin lesion"):
        with open(image_path, "rb") as f:
            response = requests.post(
                f"{self.api_url}/analyze/image",
                files={"file": f},
                params={"image_type": image_type}
            )
        return response.json()

# Usage
client = MedLensClient()
result = client.query("Fever and headache")
print(result["response"])
```

## 🚨 Common Scenarios

### Scenario: First Query Takes Long Time
**Reason**: Model downloading (~4GB)
**Solution**: Wait for download to complete (one-time)

### Scenario: No Sources in Response
**Reason**: No guidelines uploaded or query doesn't match
**Solution**: Upload relevant medical guidelines PDFs

### Scenario: Rate Limit Error
**Reason**: Too many requests
**Solution**: Wait 1 hour or increase limit in config

### Scenario: Out of Memory
**Reason**: Insufficient RAM
**Solution**: Use CPU mode, close other apps, reduce chunk size

## 📚 Additional Resources

- **Setup Guide**: See `LOCAL_SETUP.md`
- **Troubleshooting**: See `TROUBLESHOOTING.md`
- **Quick Start**: See `QUICKSTART.md`
- **API Documentation**: http://localhost:8000/docs (when running)

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Can make symptom queries
- [ ] Can upload and ingest PDFs
- [ ] Can analyze images
- [ ] Query history works
- [ ] Statistics are tracked
- [ ] All features functional

---

**Ready to use!** Start with a simple query and explore the features.
