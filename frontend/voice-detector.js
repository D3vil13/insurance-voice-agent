/**
 * Voice Activity Detector
 * Detects when user is speaking and when they stop (silence detection)
 */
class VoiceActivityDetector {
    constructor(stream, options = {}) {
        this.stream = stream;
        this.options = {
            silenceThreshold: options.silenceThreshold || 0.02,
            silenceDuration: options.silenceDuration || 2000, // 2 seconds
            checkInterval: options.checkInterval || 100, // 100ms
            ...options
        };

        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.isActive = false;
        this.isSpeaking = false;
        this.silenceStart = null;
        this.checkIntervalId = null;

        // Event callbacks
        this.onvoicestart = null;
        this.onvoiceend = null;
        this.onsilence = null;
        this.onactivity = null;

        this.init();
    }

    init() {
        // Create audio context and analyser
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 2048;
        this.analyser.smoothingTimeConstant = 0.8;

        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);

        // Connect stream to analyser
        const source = this.audioContext.createMediaStreamSource(this.stream);
        source.connect(this.analyser);
    }

    start() {
        if (this.isActive) return;

        this.isActive = true;
        this.isSpeaking = false;
        this.silenceStart = null;

        // Start checking for voice activity
        this.checkIntervalId = setInterval(() => {
            this.checkVoiceActivity();
        }, this.options.checkInterval);
    }

    stop() {
        if (!this.isActive) return;

        this.isActive = false;

        if (this.checkIntervalId) {
            clearInterval(this.checkIntervalId);
            this.checkIntervalId = null;
        }
    }

    checkVoiceActivity() {
        if (!this.isActive) return;

        // Get current audio level
        this.analyser.getByteTimeDomainData(this.dataArray);

        // Calculate RMS (root mean square) for volume level
        let sum = 0;
        for (let i = 0; i < this.dataArray.length; i++) {
            const normalized = (this.dataArray[i] - 128) / 128;
            sum += normalized * normalized;
        }
        const rms = Math.sqrt(sum / this.dataArray.length);

        // Emit activity level
        if (this.onactivity) {
            this.onactivity(rms);
        }

        // Check if voice is detected
        const hasVoice = rms > this.options.silenceThreshold;

        if (hasVoice) {
            // Voice detected
            if (!this.isSpeaking) {
                this.isSpeaking = true;
                this.silenceStart = null;
                if (this.onvoicestart) {
                    this.onvoicestart();
                }
            } else {
                // Reset silence timer
                this.silenceStart = null;
            }
        } else {
            // No voice detected
            if (this.isSpeaking) {
                // User was speaking, now silent
                if (this.silenceStart === null) {
                    this.silenceStart = Date.now();
                } else {
                    // Check if silence duration exceeded
                    const silenceDuration = Date.now() - this.silenceStart;
                    if (silenceDuration >= this.options.silenceDuration) {
                        this.isSpeaking = false;
                        this.silenceStart = null;

                        if (this.onsilence) {
                            this.onsilence();
                        }
                        if (this.onvoiceend) {
                            this.onvoiceend();
                        }
                    }
                }
            }
        }
    }

    getAudioLevel() {
        if (!this.analyser) return 0;

        this.analyser.getByteTimeDomainData(this.dataArray);
        let sum = 0;
        for (let i = 0; i < this.dataArray.length; i++) {
            const normalized = (this.dataArray[i] - 128) / 128;
            sum += normalized * normalized;
        }
        return Math.sqrt(sum / this.dataArray.length);
    }

    destroy() {
        this.stop();
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
    }
}
