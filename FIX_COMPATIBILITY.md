# Fixing PyTorch/Transformers Compatibility Error

## 🐛 Error You're Seeing

```
AttributeError: module 'torch.utils._pytree' has no attribute 'register_pytree_node'
```

This is a **version compatibility issue** between PyTorch and transformers.

## ✅ Quick Fix (Recommended)

Run the automated fix script:

```bash
python scripts/fix_dependencies.py
```

Then restart your backend:
```bash
python run_api.py
```

## 🔧 Manual Fix

If the script doesn't work, fix manually:

### Step 1: Uninstall Conflicting Packages
```bash
pip uninstall torch transformers accelerate -y
```

### Step 2: Install Compatible Versions
```bash
# Install PyTorch 2.1+ (CPU version - works everywhere)
pip install torch>=2.1.0,<2.5.0 --index-url https://download.pytorch.org/whl/cpu

# Or if you have CUDA GPU:
pip install torch>=2.1.0,<2.5.0 --index-url https://download.pytorch.org/whl/cu118

# Install transformers
pip install transformers>=4.35.0,<5.0.0

# Install accelerate
pip install accelerate>=0.24.0
```

### Step 3: Verify Installation
```bash
python -c "import torch; import transformers; print(f'PyTorch: {torch.__version__}'); print(f'Transformers: {transformers.__version__}')"
```

### Step 4: Restart Backend
```bash
python run_api.py
```

## 🎯 Root Cause

- **Transformers 4.35+** requires **PyTorch 2.1+** for pytree functionality
- Your current PyTorch version is likely < 2.1
- The `register_pytree_node` function was added in PyTorch 2.1

## 🔍 Check Your Versions

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

**Required:**
- PyTorch: 2.1.0 or higher
- Transformers: 4.35.0 or higher

## 💡 Prevention

The `requirements.txt` has been updated with compatible version ranges:
- `torch>=2.1.0,<2.5.0`
- `transformers>=4.35.0,<5.0.0`

Always install from `requirements.txt`:
```bash
pip install -r requirements.txt
```

## 🆘 Still Having Issues?

1. **Create fresh virtual environment:**
   ```bash
   python -m venv venv_new
   source venv_new/bin/activate  # or venv_new\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Check compatibility:**
   ```bash
   python app/compatibility_check.py
   ```

3. **Use CPU-only PyTorch** (more compatible):
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

## ✅ Success Indicators

After fixing, you should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

No errors about `register_pytree_node`!
