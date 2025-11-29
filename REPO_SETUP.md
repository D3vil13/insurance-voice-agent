# 📦 Repository Setup Guide

## 🔗 Cloning the Repository

### Option 1: Clone from Git

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/insurance-voice-agent.git

# Navigate to project directory
cd insurance-voice-agent

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Download ZIP

1. Download the ZIP file from GitHub
2. Extract to your desired location
3. Open terminal in extracted folder
4. Run: `pip install -r requirements.txt`

---

## 📋 What's in requirements.txt

The `requirements.txt` file contains all Python dependencies organized by category:

### Web Framework
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `python-multipart` - File upload support

### Database & AI
- `chromadb` - Vector database (pre-populated with 152 insurance docs)
- `sentence-transformers` - Text embeddings
- `langchain-community` - LangChain integrations

### Voice Processing
- `faster-whisper` - Speech-to-text (STT)
- `google-cloud-texttospeech` - Text-to-speech (TTS)
- `sounddevice` - Audio input/output
- `soundfile` - Audio file handling

### LLM Integration
- `requests` - HTTP client for OpenRouter API
- `langgraph` - LangGraph workflow

### Utilities
- `python-dotenv` - Environment variables
- `numpy` - Numerical operations
- `pydantic` - Data validation

---

## 🚀 Quick Start After Clone

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
# Edit apikeys.env and add your OpenRouter API key

# 3. Run the app
.\start_local.bat
```

---

## 📝 Notes

- **Total packages:** ~15 main dependencies + their sub-dependencies (~50 total)
- **Installation time:** 2-5 minutes (depending on internet speed)
- **Disk space:** ~2GB (including Python packages)
- **Google Cloud TTS:** Optional (app has fallback TTS services)

---

## 🔄 Updating Dependencies

```powershell
# Update all packages to latest versions
pip install -r requirements.txt --upgrade

# Or update specific package
pip install fastapi --upgrade
```

---

## ✅ Verify Installation

```powershell
# Check if all packages installed correctly
pip list

# Test backend
python api_server.py
# Should start on http://localhost:8000

# Test frontend
cd frontend
python -m http.server 3000
# Should start on http://localhost:3000
```

---

For complete setup instructions, see **[LOCAL_SETUP.md](file:///c:/Users/d3vsh/Downloads/backupMH/LOCAL_SETUP.md)**
