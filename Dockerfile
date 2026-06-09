FROM python:3.11-slim

WORKDIR /app

# Install system deps (ffmpeg + libsndfile needed for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download sentence-transformers model for faster cold starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application code
COPY config.py .
COPY utils.py .
COPY stt_service.py .
COPY tts_service.py .
COPY api_server.py .

# Copy ChromaDB database (read-only RAG)
COPY chroma_insurance_db ./chroma_insurance_db

# Create directories for logs and audio
RUN mkdir -p logs/audio_segments /tmp/api_audio_output

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["python", "api_server.py"]
