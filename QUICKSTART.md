# 🚀 Quick Start Guide

## One-Command Startup

```powershell
.\start_local.bat
```

That's it! The script will:
- ✅ Check Python installation
- ✅ Install dependencies (if needed)
- ✅ Start backend (port 8000)
- ✅ Start frontend (port 3000)
- ✅ Open browser automatically

---

## URLs

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## First Time Setup

1. Install Python 3.11+
2. Get OpenRouter API key from https://openrouter.ai/
3. Edit `apikeys.env`:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```
4. Run `.\start_local.bat`

---

## Troubleshooting

### Port Already in Use
```powershell
netstat -ano | findstr ":8000 :3000"
taskkill /F /PID <PID>
```

### Frontend Shows "Disconnected"
- Check backend is running: http://localhost:8000/health
- Restart both servers

### Microphone Not Working
- Allow microphone in browser permissions
- Use Chrome or Edge

---

## Stopping

Close both terminal windows or press `Ctrl+C` in each.

---

For detailed documentation, see `LOCAL_SETUP.md`
