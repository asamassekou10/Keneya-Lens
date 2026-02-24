# MedLens Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Backend
```bash
# Option 1: Use convenience script
python run_api.py

# Option 2: Direct uvicorn
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Frontend (New Terminal)
```bash
# Option 1: Use convenience script
python run_streamlit.py

# Option 2: Direct streamlit
streamlit run app/streamlit_app.py
```

### Step 4: Open Browser
Navigate to: `http://localhost:8501`

## 📋 First Steps

1. **Wait for model download** (first run only, ~4GB)
   - The model will download automatically from HuggingFace
   - This happens when you make your first query

2. **Upload medical guidelines** (optional but recommended)
   - Use the sidebar "Upload Medical Guidelines" section
   - Upload a PDF with medical protocols or guidelines
   - Wait for processing confirmation

3. **Test a query**
   - Enter symptoms in the main text area
   - Click "Analyze Symptoms"
   - Review the response and sources

## 🧪 Test the Engine

Run the test script to verify everything works:
```bash
python test_engine.py
```

## ⚙️ Configuration

Edit `config.py` or set environment variables:
- `MEDGEMMA_MODEL`: Model name (default: `google/gemma-2-2b-it`)
- `DEVICE`: `auto`, `cpu`, or `cuda`
- `API_PORT`: Backend port (default: 8000)
- `STREAMLIT_PORT`: Frontend port (default: 8501)

## 📝 Notes

- **First Run**: Model download takes time (~4GB for Gemma 2B)
- **Memory**: Requires 8GB+ RAM (16GB recommended)
- **GPU**: Optional but speeds up inference significantly
- **Offline**: Works completely offline after initial model download

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify all dependencies are installed
- Check Python version (3.8+)

### Model loading fails
- Check internet connection (first download only)
- Verify sufficient disk space (~4GB)
- Try setting `DEVICE=cpu` in config.py

### Streamlit can't connect to API
- Ensure backend is running on port 8000
- Check `API_BASE_URL` in `app/streamlit_app.py`
- Verify firewall settings

## 📚 Next Steps

- Upload medical guidelines PDFs for better context
- Customize the system prompt in `app/medgemma_engine.py`
- Adjust generation parameters (temperature, max_tokens)
- Add more medical reference documents
