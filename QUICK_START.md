# Quick Start Guide - Auto Voice Detection

## 🚀 Start the Backend Server

```bash
cd c:\Users\d3vsh\Downloads\backupMH
python api_server.py
```

The server will start on `http://localhost:8000`

## 🌐 Open the Frontend

Open `frontend/index.html` in your browser, or use a live server.

If using VS Code Live Server:
1. Right-click on `frontend/index.html`
2. Select "Open with Live Server"

## ✅ Test the Auto Voice Detection

### Step 1: Start Call
1. Click the **"Start Call"** button (📞)
2. Allow microphone access when prompted
3. **Listen** - The greeting will play automatically:
   > "Hi, this is PolicyPal AI from ICICI Lombard Insurance. How can I help you today?"

### Step 2: Speak Your Question
1. After the greeting ends, the system **automatically starts listening**
2. Speak your question (e.g., "What is motor insurance?")
3. **Stop speaking** - The system will automatically detect silence and stop recording after 2 seconds

### Step 3: Get Response
1. Your question appears in the chat
2. The AI response appears and **plays automatically**
3. After the response, the system **automatically starts listening again**

### Step 4: Continue Conversation
1. Ask follow-up questions
2. The cycle repeats seamlessly - **no clicking required!**

### Step 5: End Call
1. Click **"End Call"** button when done
2. The call ends gracefully

## 🎯 What's Different Now?

| Before | After |
|--------|-------|
| Click "Record" → Speak → Click "Stop" | Click "Start Call" → Speak → Auto-stops |
| Manual for each turn | Automatic for all turns |
| No greeting | Greeting plays automatically |
| Disconnected experience | Seamless conversation |

## 🔧 Troubleshooting

### Microphone not working?
- Check browser permissions (chrome://settings/content/microphone)
- Ensure no other app is using the microphone

### Greeting not playing?
- Check if TTS service is working: `python -c "from tts_service import tts_with_fallback; print('TTS OK')"`
- Check browser console for errors

### Auto-detection not stopping?
- Speak louder or closer to microphone
- Adjust silence threshold in `voice-detector.js` if needed

## 📊 Expected Behavior

✅ Button changes: "Start Call" → "End Call"  
✅ Greeting plays automatically  
✅ Recording starts automatically after greeting  
✅ Visualizer bars animate while speaking  
✅ Recording stops after 2s of silence  
✅ Response plays automatically  
✅ Next recording starts automatically  
✅ Seamless multi-turn conversation  

Enjoy your seamless voice AI assistant! 🎉
