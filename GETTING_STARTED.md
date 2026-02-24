# 🚀 Getting Started with MedLens

## Welcome!

This guide will help you get MedLens running locally in minutes.

## 📋 Choose Your Path

### 🟢 I'm New - Show Me Everything
→ Start with **[LOCAL_SETUP.md](LOCAL_SETUP.md)** for complete setup instructions

### 🟡 I Just Want to Run It Fast
→ Use **[QUICKSTART.md](QUICKSTART.md)** for 5-minute setup

### 🔵 I Want to Use It Programmatically
→ Check **[USAGE_GUIDE.md](USAGE_GUIDE.md)** for API examples

### 🔴 I'm Having Problems
→ See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for solutions

## ⚡ Super Quick Start (Copy-Paste)

```bash
# 1. Verify setup
python scripts/setup_check.py

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start everything
python scripts/start_all.py

# 4. Open browser: http://localhost:8501
```

That's it! The model will download automatically on first use.

## 📚 Documentation Map

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **README.md** | Overview & features | First time reading about project |
| **LOCAL_SETUP.md** | Complete setup guide | Setting up for first time |
| **QUICKSTART.md** | Fast setup | Quick reference |
| **USAGE_GUIDE.md** | How to use features | Learning to use the app |
| **TROUBLESHOOTING.md** | Fix problems | When something breaks |
| **CHANGELOG.md** | What's new | Seeing recent changes |
| **IMPROVEMENTS.md** | Future plans | Understanding roadmap |

## 🎯 Common Tasks

### Task: First Time Setup
1. Read [LOCAL_SETUP.md](LOCAL_SETUP.md)
2. Run `python scripts/setup_check.py`
3. Install dependencies
4. Start services
5. Make test query

### Task: Daily Usage
1. Start backend: `python run_api.py`
2. Start frontend: `python run_streamlit.py`
3. Use web interface

### Task: API Integration
1. Read [USAGE_GUIDE.md](USAGE_GUIDE.md)
2. Check API docs: http://localhost:8000/docs
3. Use examples provided

### Task: Fix Issues
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Run setup check: `python scripts/setup_check.py`
3. Check logs in backend terminal

## 🛠️ Helpful Scripts

All scripts are in the `scripts/` directory:

- **setup_check.py** - Verify your setup is correct
- **start_all.py** - Start both backend and frontend
- **download_sample_data.py** - Create sample PDF for testing

## ✅ Verification Checklist

After setup, verify:

- [ ] `python scripts/setup_check.py` passes all checks
- [ ] Backend starts: `python run_api.py`
- [ ] Frontend starts: `python run_streamlit.py`
- [ ] Can access: http://localhost:8501
- [ ] Can make a test query
- [ ] Query appears in history

## 🎓 Learning Path

1. **Day 1**: Setup and first query
   - Follow LOCAL_SETUP.md
   - Make your first symptom query
   - Upload a test PDF

2. **Day 2**: Explore features
   - Try image analysis
   - Review query history
   - Check statistics

3. **Day 3**: Advanced usage
   - Use API directly
   - Customize configuration
   - Integrate into your workflow

## 💡 Pro Tips

- **Keep backend running**: Start once, use many times
- **Upload guidelines**: Better results with relevant PDFs
- **Check history**: Learn from past queries
- **Use appropriate settings**: Adjust temperature/tokens for your needs

## 🆘 Need Help?

1. **Check documentation** - Most issues are covered
2. **Run setup check** - `python scripts/setup_check.py`
3. **Review logs** - Check backend terminal output
4. **See troubleshooting** - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🎉 You're Ready!

Start with [LOCAL_SETUP.md](LOCAL_SETUP.md) or jump straight to [QUICKSTART.md](QUICKSTART.md).

Happy coding! 🚀
