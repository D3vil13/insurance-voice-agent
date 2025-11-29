// Configuration
const API_URL = 'http://localhost:8000';

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const recordBtn = document.getElementById('recordBtn');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const statusMessage = document.getElementById('statusMessage');
const voiceMode = document.getElementById('voiceMode');
const textMode = document.getElementById('textMode');
const voiceInputContainer = document.getElementById('voiceInputContainer');
const textInputContainer = document.getElementById('textInputContainer');
const audioVisualizer = document.getElementById('audioVisualizer');
const connectionStatus = document.getElementById('connectionStatus');
const dbDocsCount = document.getElementById('dbDocsCount');
const queriesCount = document.getElementById('queriesCount');

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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkBackendConnection();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    voiceMode.addEventListener('click', () => switchMode('voice'));
    textMode.addEventListener('click', () => switchMode('text'));
    recordBtn.addEventListener('click', handleCallButton);
    sendBtn.addEventListener('click', sendTextQuery);
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendTextQuery();
    });

    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.dataset.question;
            switchMode('text');
            textInput.value = question;
            sendTextQuery();
        });
    });
}

// Check Backend Connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            updateConnectionStatus(true);
            dbDocsCount.textContent = data.components.database.documents;
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        console.error('Backend connection failed:', error);
        updateConnectionStatus(false);
        updateStatus('⚠️ Cannot connect to backend. Please check if the server is running.', 'warning');
    }
}

// Update Connection Status
function updateConnectionStatus(connected) {
    const dot = connectionStatus.querySelector('.status-dot');
    const text = connectionStatus.querySelector('.status-text');

    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// Switch Mode
function switchMode(mode) {
    currentMode = mode;

    if (mode === 'voice') {
        voiceMode.classList.add('active');
        textMode.classList.remove('active');
        voiceInputContainer.classList.remove('hidden');
        textInputContainer.classList.add('hidden');
    } else {
        textMode.classList.add('active');
        voiceMode.classList.remove('active');
        textInputContainer.classList.remove('hidden');
        voiceInputContainer.classList.add('hidden');
    }
}

// Handle Call Button (Start/End Call)
async function handleCallButton() {
    if (isInCall) {
        endCall();
    } else {
        await startCall();
    }
}

// Start Call
async function startCall() {
    try {
        updateStatus('📞 Starting call...', 'info');

        // Request microphone access
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Call backend to get greeting
        const response = await fetch(`${API_URL}/api/start-call`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentSessionId = data.session_id;

        // Display greeting in chat
        addMessage(data.greeting_text, 'agent', data.greeting_audio_url);

        // Play greeting audio
        if (data.greeting_audio_url) {
            updateStatus('🔊 Playing greeting...', 'info');
            await playAudioAndWait(`${API_URL}${data.greeting_audio_url}`);
        }

        // Update UI to "In Call" state
        isInCall = true;
        recordBtn.classList.add('in-call');
        recordBtn.querySelector('.record-icon').textContent = '📴';
        recordBtn.querySelector('.record-text').textContent = 'End Call';

        // Start listening automatically after greeting
        await startAutoRecording();

    } catch (error) {
        console.error('Error starting call:', error);
        updateStatus('❌ Failed to start call. Please check microphone permissions.', 'error');
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
    }
}

// End Call
function endCall() {
    // Stop recording if active
    if (isRecording) {
        stopAutoRecording();
    }

    // Stop voice detector
    if (voiceDetector) {
        voiceDetector.destroy();
        voiceDetector = null;
    }

    // Stop media stream
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    // Update UI
    isInCall = false;
    isProcessing = false;
    recordBtn.classList.remove('in-call');
    recordBtn.querySelector('.record-icon').textContent = '📞';
    recordBtn.querySelector('.record-text').textContent = 'Start Call';
    audioVisualizer.classList.remove('active');

    updateStatus('📴 Call ended', 'info');

    // Add farewell message
    addMessage('Thank you for calling ICICI Lombard Insurance. Have a great day!', 'agent');
}

// Start Auto Recording with Voice Detection
async function startAutoRecording() {
    if (!mediaStream || isProcessing) return;

    try {
        // Initialize voice detector
        voiceDetector = new VoiceActivityDetector(mediaStream, {
            silenceThreshold: 0.02,
            silenceDuration: 2000, // 2 seconds of silence
            checkInterval: 100
        });

        // Set up voice detector callbacks
        voiceDetector.onvoicestart = () => {
            console.log('Voice detected - started speaking');
        };

        voiceDetector.onsilence = () => {
            console.log('Silence detected - stopping recording');
            stopAutoRecording();
        };

        voiceDetector.onactivity = (level) => {
            // Update visualizer based on voice activity
            updateVisualizer(level);
        };

        // Start voice detection
        voiceDetector.start();

        // Initialize MediaRecorder
        audioChunks = [];
        mediaRecorder = new MediaRecorder(mediaStream);

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await processAudioQuery(audioBlob);
        };

        // Start recording
        mediaRecorder.start();
        isRecording = true;

        audioVisualizer.classList.add('active');
        updateStatus('🎤 Listening... (speak now, will auto-stop after 2s of silence)', 'info');

    } catch (error) {
        console.error('Error starting auto recording:', error);
        updateStatus('❌ Error starting recording', 'error');
    }
}

// Stop Auto Recording
function stopAutoRecording() {
    if (!isRecording) return;

    isRecording = false;

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }

    if (voiceDetector) {
        voiceDetector.stop();
    }

    audioVisualizer.classList.remove('active');
    updateStatus('⏳ Processing your audio...', 'info');
}

// Process Audio Query
async function processAudioQuery(audioBlob) {
    if (!isInCall || isProcessing) return;

    isProcessing = true;
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
        const response = await fetch(`${API_URL}/api/process-audio`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        addMessage(data.user_text, 'user');
        addMessage(data.agent_response, 'agent', data.audio_url);

        totalQueries++;
        queriesCount.textContent = totalQueries;

        updateStatus('✅ Response received!', 'success');

        // Play response audio
        if (data.audio_url) {
            await playAudioAndWait(`${API_URL}${data.audio_url}`);
        }

        // After response, start listening again automatically
        isProcessing = false;
        if (isInCall) {
            await startAutoRecording();
        }

    } catch (error) {
        console.error('Audio processing error:', error);
        updateStatus('❌ Error processing audio. Please try again.', 'error');
        isProcessing = false;

        // Restart listening on error
        if (isInCall) {
            setTimeout(() => startAutoRecording(), 1000);
        }
    }
}

// Play Audio and Wait for Completion
function playAudioAndWait(audioUrl) {
    return new Promise((resolve, reject) => {
        const audio = new Audio(audioUrl);

        audio.onended = () => {
            resolve();
        };

        audio.onerror = (error) => {
            console.error('Audio playback error:', error);
            reject(error);
        };

        audio.play().catch(error => {
            console.error('Audio play error:', error);
            reject(error);
        });
    });
}

// Update Visualizer
function updateVisualizer(level) {
    const bars = audioVisualizer.querySelectorAll('.visualizer-bar');
    const intensity = Math.min(level * 50, 1); // Scale the level

    bars.forEach((bar, index) => {
        const height = Math.random() * intensity * 100;
        bar.style.height = `${Math.max(height, 10)}%`;
    });
}

// Send Text Query
async function sendTextQuery() {
    const text = textInput.value.trim();

    if (!text) {
        updateStatus('⚠️ Please enter a question', 'warning');
        return;
    }

    textInput.value = '';
    addMessage(text, 'user');
    updateStatus('⏳ Thinking...', 'info');

    try {
        const response = await fetch(`${API_URL}/api/text-query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        addMessage(data.agent_response, 'agent');

        totalQueries++;
        queriesCount.textContent = totalQueries;

        updateStatus('✅ Response received!', 'success');

    } catch (error) {
        console.error('Text query error:', error);
        updateStatus('❌ Error processing query. Please try again.', 'error');
    }
}

// Add Message to Chat
function addMessage(text, sender, audioUrl = null) {
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = sender === 'user' ? 'You' : 'AI Assistant';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(textDiv);

    if (audioUrl && sender === 'agent') {
        const audioPlayer = document.createElement('div');
        audioPlayer.className = 'audio-player';
        audioPlayer.innerHTML = `
            <audio controls>
                <source src="${audioUrl}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        `;
        messageDiv.appendChild(audioPlayer);
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update Status Message
function updateStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.style.color = type === 'error' ? 'var(--danger-color)' :
        type === 'success' ? 'var(--success-color)' :
            type === 'warning' ? 'var(--warning-color)' :
                'var(--text-secondary)';

    setTimeout(() => {
        statusMessage.textContent = '';
    }, 5000);
}
