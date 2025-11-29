# 🛡️ Insurance Voice Agent - Local Setup

**PolicyPal AI** - An AI-powered voice assistant for insurance customer service.

---

## 🚀 Quick Start (One Command)

```powershell
# Run this single command to start everything:
.\start_local.bat
```

This will:
1. Start the backend API server (port 8000)
2. Start the frontend web server (port 3000)
3. Open your browser to http://localhost:3000

---

## 📋 Prerequisites

### Required Software
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Git** (optional) - For version control

### Check if Python is installed:
```powershell
python --version
```

---

## 🔧 Installation Steps

### Step 1: Clone the Repository

**If you have the repository on GitHub/GitLab:**

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/insurance-voice-agent.git

# Navigate to project directory
cd insurance-voice-agent
```

**If you downloaded as ZIP:**

```powershell
# Extract the ZIP file
# Navigate to the extracted folder
cd c:\Users\d3vsh\Downloads\backupMH
```

---

### Step 2: Install Dependencies

```powershell
# Install Python packages
pip install -r requirements.txt
```

**This will install (~15 packages):**

**This will install:**
- FastAPI (web framework)
- ChromaDB (vector database)
- Faster Whisper (speech-to-text)
- Google Cloud TTS (text-to-speech)
- OpenRouter (LLM integration)
- And other dependencies

---

### Step 3: Configure API Keys

Edit `apikeys.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Get your OpenRouter API key:**
1. Go to https://openrouter.ai/
2. Sign up for free account
3. Get your API key from dashboard
4. Paste it in `apikeys.env`

---

## 🎯 Running the Application

### Option 1: One-Click Start (Recommended)

Double-click `start_local.bat` or run:

```powershell
.\start_local.bat
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
python api_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
python -m http.server 3000
```

**Then open:** http://localhost:3000

---

## 🧪 Testing the Application

### 1. Check Backend Health
Open: http://localhost:8000/health

Should show:
```json
{
  "status": "healthy",
  "components": {
    "database": { "documents": 152 }
  }
}
```

### 2. Test Frontend
Open: http://localhost:3000

- **Connection Status:** Should show "Connected" (green dot)
- **Database Docs:** Should show document count

### 3. Test Text Mode
1. Click "Text" mode
2. Type: "What is covered under motor insurance?"
3. Click send
4. You should get a response! ✅

### 4. Test Voice Mode
1. Click "Voice" mode
2. Click "Start Call"
3. Allow microphone access
4. Speak your question
5. Wait 2 seconds of silence
6. You should hear the AI response! ✅

---

## 📁 Project Structure

```
backupMH/
├── api_server.py              # Backend API server
├── config.py                  # Configuration settings
├── utils.py                   # RAG and LLM functions
├── stt_service.py             # Speech-to-text service
├── tts_service.py             # Text-to-speech service
├── nodes.py                   # LangGraph nodes
├── graph.py                   # LangGraph workflow
├── state.py                   # State management
├── session_utils.py           # Session utilities
├── requirements.txt           # Python dependencies
├── apikeys.env                # API keys (DO NOT COMMIT)
├── start_local.bat            # One-click startup script
│
├── chroma_insurance_db/       # Vector database (152 documents)
├── frontend/                  # Web interface
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── voice-detector.js
│
├── logs/                      # Application logs
└── api_audio_output/          # Generated audio files
```

---

## ⚙️ Configuration

### Change LLM Model

Edit `config.py`:

```python
LLM_MODEL = "openai/gpt-3.5-turbo"  # Fast and cheap
# or
LLM_MODEL = "anthropic/claude-3-haiku"  # Better quality
```

### Change Voice Settings

Edit `config.py`:

```python
VOICE_ACTIVITY_THRESHOLD = 0.02  # Lower = more sensitive
SAMPLE_RATE = 16000              # Audio quality
```

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `Port 8000 already in use`

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /F /PID <PID>
```

---

### Frontend won't start

**Error:** `Port 3000 already in use`

**Solution:**
```powershell
# Find and kill process on port 3000
netstat -ano | findstr :3000
taskkill /F /PID <PID>
```

---

### "Disconnected" status on frontend

**Causes:**
1. Backend not running
2. Wrong API URL in frontend

**Solution:**
```powershell
# Check backend is running
curl http://localhost:8000/health

# Verify frontend API_URL in frontend/app.js (line 2)
# Should be: const API_URL = 'http://localhost:8000';
```

---

### Microphone not working

**Causes:**
1. Browser permissions denied
2. No microphone connected

**Solution:**
1. Check browser permissions (click lock icon in address bar)
2. Allow microphone access
3. Try Chrome or Edge (best compatibility)
4. Check Windows microphone settings

---

### LLM responses are slow (6-8 seconds)

**Solutions:**
1. Use faster model: `openai/gpt-3.5-turbo`
2. Reduce max tokens in `config.py`
3. Check internet connection

---

### TTS not working

**Error:** `Google Cloud credentials not found`

**This is normal!** The app will fallback to other TTS services automatically.

---

## 🔑 API Keys & Services

### Required:
- **OpenRouter API Key** - For LLM responses
  - Get it: https://openrouter.ai/
  - Free tier available
  - Cost: ~$0.001 per request

### Optional:
- **Google Cloud TTS** - For better voice quality
  - Not required (app has fallbacks)
  - Setup: https://cloud.google.com/text-to-speech/docs/quickstart

---

## 📊 Database Information

The project includes a pre-populated ChromaDB with **152 insurance documents** covering:
- Motor insurance policies
- Health insurance coverage
- Claim procedures
- Premium calculations
- Policy renewals
- General insurance FAQs

**Location:** `chroma_insurance_db/`

---

## 🛑 Stopping the Application

### If using start_local.bat:
Press `Ctrl+C` in both terminal windows

### Manual stop:
```powershell
# Find and kill processes
netstat -ano | findstr ":8000 :3000"
taskkill /F /PID <backend_PID>
taskkill /F /PID <frontend_PID>
```

---

## 📝 Logs

Application logs are saved in:
- `logs/` - General application logs
- `logs/audio_segments/` - Audio processing logs

View recent logs:
```powershell
Get-Content logs\*.log -Tail 50
```

---

## 🎓 Usage Tips

### Best Practices:
1. **Speak clearly** - Wait for "Listening..." message
2. **Pause 2 seconds** - After speaking to trigger auto-stop
3. **Ask specific questions** - "What does motor insurance cover?"
4. **Use text mode** - For testing or when microphone unavailable

### Example Questions:
- "What is covered under motor insurance?"
- "How do I file a claim?"
- "What is the renewal process?"
- "What are the premium calculation factors?"

---

## 🔄 Updating the Application

```powershell
# Pull latest changes (if using Git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the application
.\start_local.bat
```

---

## 💡 Performance Notes

**Response Times:**
- Text mode: 3-5 seconds
- Voice mode: 6-8 seconds (includes STT + LLM + TTS)

**Resource Usage:**
- RAM: ~500MB (backend) + ~100MB (frontend)
- CPU: Low (spikes during audio processing)
- Disk: ~2GB (including dependencies)

---

## 🆘 Need Help?

1. **Check logs:** `logs/` directory
2. **Test backend:** http://localhost:8000/docs
3. **Browser console:** Press F12 to see errors
4. **Restart everything:** Close all terminals and run `start_local.bat` again

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 🎉 You're Ready!

Run `.\start_local.bat` and start chatting with PolicyPal AI! 🚀
