"""
Configuration and Constants for Voice Agent
"""
import os
from dotenv import load_dotenv

# ========== PATHS ==========
APIKEYS_PATH = "c:\\Users\\d3vsh\\Downloads\\backupMH\\apikeys.env"
CHROMA_DB_PATH = "c:\\Users\\d3vsh\\Downloads\\backupMH\\chroma_insurance_db"
GOOGLE_CREDENTIALS_PATH = "C:\\Users\\d3vsh\\Downloads\\api\\yt-api-395217-0687a63c2087.json"

# ========== AUDIO SETTINGS ==========
SAMPLE_RATE = 16000
MAX_RECORDING_DURATION = 15  # seconds
SILENCE_DURATION = 2.0  # seconds
VOICE_ACTIVITY_THRESHOLD = 0.02

# ========== CONVERSATION SETTINGS ==========
MAX_TURNS = 5
DEFAULT_MAX_TOKENS = 150
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.9

# ========== LLM SETTINGS ==========
LLM_MODEL = "openai/gpt-4o-mini"
RAG_TOP_K = 3

# ========== EMBEDDER SETTINGS ==========
EMBEDDER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ========== LOAD ENVIRONMENT VARIABLES ==========
load_dotenv(APIKEYS_PATH)
OPENROUTER_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH
