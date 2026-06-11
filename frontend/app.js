const API_URL = (() => {
    const saved = localStorage.getItem('API_URL');
    if (saved) return saved;
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    return 'https://ai-voice-agent-fjqi.onrender.com';
})();

// DOM
const chatContainer = document.getElementById('chatContainer');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const statusMsg = document.getElementById('statusMessage');
const callBtn = document.getElementById('callBtn');
const voiceStatus = document.getElementById('voiceStatus');
const visualizerWrap = document.getElementById('visualizerWrap');
const voiceInputWrap = document.getElementById('voiceInputWrap');
const textInputWrap = document.getElementById('textInputWrap');
const modeTabs = document.getElementById('modeTabs');
const connectionStatus = document.getElementById('connectionStatus');
const dbDocsCount = document.getElementById('dbDocsCount');
const queriesCount = document.getElementById('queriesCount');
const sarvamInput = document.getElementById('sarvamApiKey');
const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
const toast = document.getElementById('toast');

// State
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let currentMode = 'voice';
let totalQueries = 0;
let voiceDetector = null;
let mediaStream = null;
let currentSessionId = null;
let isInCall = false;
let isProcessing = false;
let sarvamApiKey = localStorage.getItem('SARVAM_API_KEY') || '';
let audioMimeType = '';
let toastTimer = null;

function getSupportedAudioMimeType() {
    const types = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/wav',
    ];
    for (const t of types) {
        if (MediaRecorder.isTypeSupported(t)) return t;
    }
    return 'audio/webm';
}

async function fetchWithTimeout(url, options, timeoutMs = 30000) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(url, { ...options, signal: controller.signal });
        return res;
    } finally {
        clearTimeout(timeout);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (sarvamInput && sarvamApiKey) {
        sarvamInput.value = sarvamApiKey;
    }
    checkBackendConnection();
    setupEventListeners();
});

function getHeaders(extra = {}) {
    const headers = { ...extra };
    if (sarvamApiKey) {
        headers['X-API-Key'] = sarvamApiKey;
    }
    return headers;
}

function showToast(msg, type = '') {
    toast.textContent = msg;
    toast.className = 'toast' + (type ? ' ' + type : '');
    clearTimeout(toastTimer);
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
}

function setupEventListeners() {
    // Mode tabs
    modeTabs.addEventListener('click', (e) => {
        const tab = e.target.closest('.mode-tab');
        if (!tab) return;
        const mode = tab.dataset.mode;
        switchMode(mode);
    });

    callBtn.addEventListener('click', handleCallButton);
    sendBtn.addEventListener('click', sendTextQuery);
    textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendTextQuery();
        }
    });

    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.dataset.question;
            switchMode('text');
            textInput.value = question;
            sendTextQuery();
        });
    });

    if (saveApiKeyBtn) {
        saveApiKeyBtn.addEventListener('click', handleApiKeySave);
    }
}

async function handleApiKeySave() {
    const key = sarvamInput ? sarvamInput.value.trim() : '';
    if (!key) {
        sarvamApiKey = '';
        localStorage.removeItem('SARVAM_API_KEY');
        saveApiKeyBtn.textContent = 'Cleared';
        saveApiKeyBtn.classList.add('saved');
        showToast('API key cleared', 'success');
        setTimeout(() => {
            saveApiKeyBtn.textContent = 'Save Key';
            saveApiKeyBtn.classList.remove('saved');
        }, 2000);
        return;
    }
    saveApiKeyBtn.textContent = 'Validating...';
    saveApiKeyBtn.disabled = true;
    try {
        const resp = await fetch(`${API_URL}/api/validate-key`, {
            method: 'POST',
            headers: { 'X-API-Key': key }
        });
        const data = await resp.json();
        if (data.valid) {
            sarvamApiKey = key;
            localStorage.setItem('SARVAM_API_KEY', key);
            saveApiKeyBtn.textContent = 'Saved!';
            saveApiKeyBtn.classList.add('saved');
            showToast('Valid API key saved', 'success');
        } else {
            showToast(`Invalid key: ${data.error || 'rejected'}`, 'error');
            saveApiKeyBtn.textContent = 'Save Key';
        }
    } catch (e) {
        showToast('Could not validate key (backend unreachable?)', 'error');
        saveApiKeyBtn.textContent = 'Save Key';
    }
    saveApiKeyBtn.disabled = false;
    setTimeout(() => {
        saveApiKeyBtn.textContent = 'Save Key';
        saveApiKeyBtn.classList.remove('saved');
    }, 2000);
}

async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_URL}/health`, { headers: getHeaders() });
        const data = await response.json();
        if (data.status === 'healthy') {
            updateConnectionStatus(true);
            if (dbDocsCount) dbDocsCount.textContent = data.components.database.documents;
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        console.error('Backend connection failed:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const dot = connectionStatus.querySelector('.status-dot');
    const text = connectionStatus.querySelector('.status-text');
    if (connected) {
        dot.className = 'status-dot connected';
        text.textContent = 'Connected';
        showToast('Connected to server', 'success');
    } else {
        dot.className = 'status-dot disconnected';
        text.textContent = 'Disconnected';
        showToast('Cannot connect to backend', 'error');
    }
}

function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.mode === mode);
    });
    voiceInputWrap.classList.toggle('hidden', mode !== 'voice');
    textInputWrap.classList.toggle('hidden', mode !== 'text');
}

async function handleCallButton() {
    if (isInCall) {
        endCall();
    } else {
        await startCall();
    }
}

async function startCall() {
    try {
        setVoiceStatus('Requesting microphone...', '');
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        setVoiceStatus('Starting call...', '');
        const response = await fetch(`${API_URL}/api/start-call`, {
            method: 'POST',
            headers: getHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentSessionId = data.session_id;
        addMessage(data.greeting_text, 'agent', data.greeting_audio_url);

        if (data.greeting_audio_url) {
            setVoiceStatus('Playing greeting...', '');
            await playAudioAndWait(`${API_URL}${data.greeting_audio_url}`);
        }

        isInCall = true;
        callBtn.classList.add('in-call');
        callBtn.textContent = '📴';

        await startAutoRecording();

    } catch (error) {
        console.error('Error starting call:', error);
        setVoiceStatus('Failed to start call. Check mic permissions.', 'error');
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
    }
}

function endCall() {
    if (isRecording) stopAutoRecording();
    if (voiceDetector) {
        voiceDetector.destroy();
        voiceDetector = null;
    }
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }
    isInCall = false;
    isProcessing = false;
    callBtn.classList.remove('in-call');
    callBtn.textContent = '📞';
    visualizerWrap.classList.remove('active');
    setVoiceStatus('Call ended', '');
    addMessage('Thank you for calling ICICI Lombard Insurance. Have a great day!', 'agent');
}

async function startAutoRecording() {
    if (!mediaStream || isProcessing) return;
    try {
        voiceDetector = new VoiceActivityDetector(mediaStream, {
            silenceThreshold: 0.02,
            silenceDuration: 2000,
            checkInterval: 100
        });

        voiceDetector.onvoicestart = () => {
            console.log('Voice started');
        };

        voiceDetector.onsilence = () => {
            console.log('Silence detected');
            stopAutoRecording();
        };

        voiceDetector.onactivity = (level) => {
            updateVisualizer(level);
        };

        voiceDetector.start();

        audioMimeType = getSupportedAudioMimeType();
        audioChunks = [];
        mediaRecorder = new MediaRecorder(mediaStream, audioMimeType ? { mimeType: audioMimeType } : {});

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: audioMimeType || 'audio/webm' });
            await processAudioQuery(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        visualizerWrap.classList.add('active');
        setVoiceStatus('Listening...', 'listening');

    } catch (error) {
        console.error('Error starting recording:', error);
        setVoiceStatus('Error starting recording', 'error');
    }
}

function stopAutoRecording() {
    if (!isRecording) return;
    isRecording = false;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    if (voiceDetector) {
        voiceDetector.stop();
    }
    visualizerWrap.classList.remove('active');
    setVoiceStatus('Processing...', 'processing');
}

async function processAudioQuery(audioBlob) {
    if (!isInCall || isProcessing) return;
    isProcessing = true;

    const formData = new FormData();
    const ext = audioMimeType.includes('webm') ? 'webm' : audioMimeType.includes('ogg') ? 'ogg' : 'wav';
    formData.append('audio', audioBlob, `recording.${ext}`);

    try {
        const response = await fetchWithTimeout(`${API_URL}/api/process-audio`, {
            method: 'POST',
            headers: getHeaders(),
            body: formData
        });

        if (!response.ok) {
            const errText = await response.text().catch(() => '');
            throw new Error(`HTTP ${response.status}: ${errText.slice(0, 200)}`);
        }

        const data = await response.json();

        if (data.warning) {
            showToast(data.warning, 'error');
        }

        addMessage(data.user_text || '(could not transcribe)', 'user');
        addMessage(data.agent_response, 'agent', data.audio_url);

        totalQueries++;
        if (queriesCount) queriesCount.textContent = totalQueries;

        if (data.audio_url) {
            setVoiceStatus('Playing response...', '');
            await playAudioAndWait(`${API_URL}${data.audio_url}`);
        }

        isProcessing = false;
        if (isInCall) {
            await startAutoRecording();
        }

    } catch (error) {
        console.error('Audio processing error:', error);
        setVoiceStatus(`Error: ${error.message.slice(0, 60)}`, 'error');
        showToast(error.message.slice(0, 80), 'error');
        isProcessing = false;
        if (isInCall) {
            setTimeout(() => startAutoRecording(), 1500);
        }
    }
}

function playAudioAndWait(audioUrl) {
    return new Promise((resolve, reject) => {
        const audio = new Audio(audioUrl);
        audio.onended = () => resolve();
        audio.onerror = (error) => {
            console.error('Audio playback error:', error);
            reject(error);
        };
        audio.play().catch(reject);
    });
}

function updateVisualizer(level) {
    const bars = visualizerWrap.querySelectorAll('.viz-bar');
    const intensity = Math.min(level * 50, 1);
    bars.forEach((bar, index) => {
        const height = Math.random() * intensity * 100;
        bar.style.height = `${Math.max(height, 8)}%`;
    });
}

function setVoiceStatus(msg, type) {
    voiceStatus.textContent = msg;
    voiceStatus.className = 'voice-status';
    if (type) voiceStatus.classList.add(type);
}

async function sendTextQuery() {
    const text = textInput.value.trim();
    if (!text) return;

    textInput.value = '';
    addMessage(text, 'user');
    statusMsg.textContent = 'Thinking...';

    try {
        const response = await fetch(`${API_URL}/api/text-query`, {
            method: 'POST',
            headers: getHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.agent_response, 'agent');

        totalQueries++;
        if (queriesCount) queriesCount.textContent = totalQueries;

        statusMsg.textContent = '';

    } catch (error) {
        console.error('Text query error:', error);
        statusMsg.textContent = 'Error processing query';
        showToast(error.message, 'error');
    }
}

function addMessage(text, sender, audioUrl = null) {
    const welcome = chatContainer.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const div = document.createElement('div');
    div.className = `message ${sender}`;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';

    const label = document.createElement('div');
    label.className = 'msg-label';
    label.textContent = sender === 'user' ? 'You' : 'AI Assistant';

    const txt = document.createElement('div');
    txt.className = 'msg-text';
    txt.textContent = text;

    bubble.appendChild(label);
    bubble.appendChild(txt);

    if (audioUrl && sender === 'agent') {
        const audioWrap = document.createElement('div');
        audioWrap.className = 'msg-audio';
        audioWrap.innerHTML = `<audio controls><source src="${API_URL}${audioUrl}" type="audio/wav"></audio>`;
        bubble.appendChild(audioWrap);
    }

    const time = document.createElement('div');
    time.className = 'msg-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    div.appendChild(bubble);
    div.appendChild(time);
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
