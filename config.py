"""
Configuration and Constants for Voice Agent
"""
import os
from dotenv import load_dotenv

# ========== PATHS ==========
# Use relative paths (works in Docker, local dev)
import sys
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_DB_PATH = os.environ.get(
    "CHROMA_DB_PATH",
    os.path.join(BASE_DIR, "chroma_insurance_db")
)

# ========== AUDIO SETTINGS ==========
SAMPLE_RATE = 16000
MAX_RECORDING_DURATION = 15
SILENCE_DURATION = 2.0
VOICE_ACTIVITY_THRESHOLD = 0.02

# ========== CONVERSATION SETTINGS ==========
MAX_TURNS = 5
DEFAULT_MAX_TOKENS = 150
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.9

# ========== LLM SETTINGS ==========
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek/deepseek-v4-flash")
RAG_TOP_K = 3

# ========== EMBEDDER SETTINGS ==========
EMBEDDER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ========== API KEYS (from environment) ==========
load_dotenv(os.path.join(BASE_DIR, "apikeys.env"))
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")

# ========== SARVAM AI SETTINGS ==========
SARVAM_STT_MODEL = "saaras:v3"
SARVAM_TTS_MODEL = "bulbul:v3"
SARVAM_TTS_SPEAKER = "shubh"
SARVAM_TTS_LANGUAGE = "en-IN"
