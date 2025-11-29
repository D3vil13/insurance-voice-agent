# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY state.py .
COPY utils.py .
COPY nodes.py .
COPY graph.py .
COPY stt_service.py .
COPY tts_service.py .
COPY session_utils.py .
COPY api_server.py .

# Copy environment file
COPY apikeys.env .

# Copy ChromaDB database
COPY chroma_insurance_db ./chroma_insurance_db

# Create directories for logs and audio
RUN mkdir -p logs/audio_segments api_audio_output

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the API server
CMD ["python", "api_server.py"]
