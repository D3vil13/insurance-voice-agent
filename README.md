# 🛡️ Insurance Voice Agent

**PolicyPal AI** - An AI-powered voice assistant for insurance customer service using RAG (Retrieval Augmented Generation).

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Quick Start

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/insurance-voice-agent.git
cd insurance-voice-agent

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp apikeys.env.example apikeys.env
# Edit apikeys.env and add your OpenRouter API key

# Run the application
.\start_local.bat
```

**That's it!** Open http://localhost:3000 in your browser.

---

## ✨ Features

- 🎤 **Voice Interaction** - Natural voice conversations with AI
- 💬 **Text Chat** - Alternative text-based interface
- 🧠 **RAG-Powered** - Retrieves information from 152 insurance documents
- 🔊 **Text-to-Speech** - Speaks responses naturally
- 🎯 **Smart Detection** - Auto-detects when you stop speaking
- 📊 **Real-time Status** - Shows connection and processing status
- 🎨 **Modern UI** - Beautiful, responsive web interface

---

## 📋 Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **OpenRouter API Key** - [Get Free Key](https://openrouter.ai/)
- **Microphone** - For voice mode (optional)

---

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/insurance-voice-agent.git
cd insurance-voice-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
# Copy example file
cp apikeys.env.example apikeys.env

# Edit apikeys.env and add your key:
# OPENROUTER_API_KEY=your_key_here
```

### 4. Run Application

**Windows:**
```powershell
.\start_local.bat
```

**Linux/Mac:**
```bash
chmod +x start_local.sh
./start_local.sh
```

---

## 📖 Documentation

- **[Local Setup Guide](LOCAL_SETUP.md)** - Complete setup instructions
- **[Quick Start](QUICKSTART.md)** - One-page reference
- **[Deployment Guide](AZURE_VERCEL_DEPLOYMENT.md)** - Deploy to Azure + Vercel
- **[Repository Setup](REPO_SETUP.md)** - Git and dependencies info

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  ← React-like vanilla JS interface
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│   FastAPI       │  ← Backend API server
│   api_server.py │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    │         │          │         │
┌───▼───┐ ┌──▼──┐  ┌────▼────┐ ┌─▼──┐
│  STT  │ │ RAG │  │   LLM   │ │TTS │
│Whisper│ │Chroma│  │OpenRouter│ │GCP│
└───────┘ └─────┘  └─────────┘ └────┘
```

---

## 🗂️ Project Structure

```
insurance-voice-agent/
├── api_server.py           # FastAPI backend server
├── config.py               # Configuration settings
├── utils.py                # RAG and LLM utilities
├── stt_service.py          # Speech-to-text service
├── tts_service.py          # Text-to-speech service
├── requirements.txt        # Python dependencies
├── start_local.bat         # Windows startup script
├── start_local.sh          # Linux/Mac startup script
│
├── frontend/               # Web interface
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── voice-detector.js
│
├── chroma_insurance_db/    # Vector database (152 docs)
└── docs/                   # Documentation
```

---

## 🎯 Usage

### Voice Mode
1. Click "Start Call"
2. Allow microphone access
3. Speak your question
4. Wait 2 seconds of silence
5. Listen to AI response

### Text Mode
1. Click "Text" tab
2. Type your question
3. Click send or press Enter
4. Read the response

### Example Questions
- "What is covered under motor insurance?"
- "How do I file a claim?"
- "What is the renewal process?"
- "What are the premium calculation factors?"

---

## 🔑 API Keys

### Required:
- **OpenRouter** - For LLM responses
  - Get free key: https://openrouter.ai/
  - Cost: ~$0.001 per request

### Optional:
- **Google Cloud TTS** - For better voice quality
  - App has fallback TTS if not configured
  - Setup: https://cloud.google.com/text-to-speech

---

## 🚀 Deployment

Deploy to production using Azure + Vercel:

```bash
# See AZURE_VERCEL_DEPLOYMENT.md for detailed instructions

# Quick deploy to Azure
az webapp up --name your-app-name --runtime "PYTHON:3.11" --sku B1

# Deploy frontend to Vercel
cd frontend
vercel --prod
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.11+
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Database:** ChromaDB (vector database)
- **STT:** Faster Whisper
- **TTS:** Google Cloud TTS (with fallbacks)
- **LLM:** OpenRouter (GPT-3.5/4, Claude, etc.)
- **Embeddings:** sentence-transformers

---

## 📊 Performance

- **Response Time:** 6-8 seconds (voice mode)
- **Response Time:** 3-5 seconds (text mode)
- **Database:** 152 pre-loaded insurance documents
- **Accuracy:** High (RAG-based responses)

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
netstat -ano | findstr ":8000 :3000"
taskkill /F /PID <PID>
```

### "Disconnected" Status
- Check backend is running: http://localhost:8000/health
- Verify API_URL in `frontend/app.js`

### Microphone Not Working
- Allow microphone in browser permissions
- Use Chrome or Edge for best compatibility

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for more troubleshooting.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@d3vil13](https://github.com/D3vil13)

---

## 🙏 Acknowledgments

- OpenRouter for LLM API access
- FastAPI for the amazing web framework
- ChromaDB for vector database
- ICICI Lombard Insurance for domain knowledge

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation in `docs/` folder
- Review troubleshooting guide in `LOCAL_SETUP.md`

---

**Made with ❤️ for better insurance customer service**
