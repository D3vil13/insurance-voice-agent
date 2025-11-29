#!/bin/bash
# Azure App Service startup script for Python deployment

# Install system dependencies (if needed)
apt-get update && apt-get install -y ffmpeg libsndfile1 portaudio19-dev || true

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs/audio_segments api_audio_output

# Start the API server
python api_server.py
