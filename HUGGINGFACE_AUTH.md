# HuggingFace Authentication Guide

## 🔐 Accessing Gated Models (Gemma)

The Gemma models are **gated** on HuggingFace, meaning you need to:
1. Request access on HuggingFace
2. Authenticate with your HuggingFace token

## ✅ Quick Setup

### Step 1: Get HuggingFace Access Token

1. **Create HuggingFace Account** (if you don't have one):
   - Go to https://huggingface.co/join

2. **Request Access to Gemma Model**:
   - Visit: https://huggingface.co/google/gemma-2-2b-it
   - Click "Agree and access repository"
   - Accept the terms of use

3. **Create Access Token**:
   - Go to: https://huggingface.co/settings/tokens
   - Click "New token"
   - Name it (e.g., "medlens-token")
   - Select "Read" permissions
   - Copy the token (starts with `hf_...`)

### Step 2: Authenticate

**Option A: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:HUGGINGFACE_TOKEN="your_token_here"

# Windows CMD
set HUGGINGFACE_TOKEN=your_token_here

# Linux/Mac
export HUGGINGFACE_TOKEN="your_token_here"
```

**Option B: HuggingFace CLI Login**
```bash
pip install huggingface_hub
huggingface-cli login
# Enter your token when prompted
```

**Option C: .env File**
Create a `.env` file in the project root:
```env
HUGGINGFACE_TOKEN=your_token_here
```

Then install python-dotenv (already in requirements.txt) and the code will load it automatically.

### Step 3: Restart Backend
```bash
python run_api.py
```

## 🔄 Alternative: Use Non-Gated Models

If you can't access Gemma, you can use alternative models:

### Option 1: Use Gemma via Google's Direct Access
Some Gemma models may be available directly from Google. Check:
- https://huggingface.co/google/gemma-2b-it (may be less restricted)

### Option 2: Use Alternative Medical Models
Edit `config.py` or set environment variable:

```python
# In config.py
MEDGEMMA_MODEL_NAME = "microsoft/DialoGPT-medium"  # Example alternative
# Or any other open model
```

### Option 3: Use Smaller Open Models
```python
# Models that don't require authentication:
MEDGEMMA_MODEL_NAME = "gpt2"  # Small, open model
# Or
MEDGEMMA_MODEL_NAME = "distilgpt2"  # Even smaller
```

**Note**: These alternatives won't be medical-specific but will work for testing.

## 🛠️ Troubleshooting

### Error: "Cannot access gated repo"
- **Solution**: You haven't authenticated or don't have access
- **Fix**: Follow Step 1 and 2 above

### Error: "401 Client Error"
- **Solution**: Invalid or expired token
- **Fix**: Generate a new token and update it

### Error: "Token not found"
- **Solution**: Environment variable not set correctly
- **Fix**: Check spelling: `HUGGINGFACE_TOKEN` (not `HF_TOKEN`)

### Verify Authentication
```bash
python -c "from huggingface_hub import whoami; print(whoami())"
```

Should show your username if authenticated.

## 📝 Code Changes

The code automatically checks for `HUGGINGFACE_TOKEN` environment variable. If set, it will use it for authentication.

You can also modify `app/medgemma_engine.py` to hardcode a token (not recommended for security):

```python
# In _load_model method, add:
from huggingface_hub import login
login(token="your_token_here")
```

## 🔒 Security Best Practices

1. **Never commit tokens to git** - Use `.env` file and add to `.gitignore`
2. **Use read-only tokens** - Don't use write tokens unless needed
3. **Rotate tokens regularly** - Generate new tokens periodically
4. **Use environment variables** - Don't hardcode tokens in code

## ✅ Success Indicators

After authenticating, you should see:
```
INFO: Loading tokenizer...
INFO: Loading model...
INFO: Model loaded successfully
```

No 401 errors!
