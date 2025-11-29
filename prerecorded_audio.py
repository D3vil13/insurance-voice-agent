"""
Pre-recorded Audio Manager
Handles detection and retrieval of pre-recorded audio files for common responses
"""
import os
from typing import Optional, Dict
from difflib import SequenceMatcher

# Base directory for pre-recorded audio
PRERECORDED_DIR = os.path.join(os.path.dirname(__file__), "prerecorded_audio")

# Mapping of common phrases to audio files
COMMON_RESPONSES = {
    "greeting": {
        "text": "Hi, this is PolicyPal AI from ICICI Lombard Insurance. How can I help you today?",
        "file": "greeting.wav",
        "threshold": 0.9  # Exact match required
    },
    "no_information": {
        "text": "I'm sorry, but I currently don't have that information.",
        "file": "common/no_information.wav",
        "threshold": 0.8
    },
    "checking": {
        "text": "Let me check that for you.",
        "file": "common/checking.wav",
        "threshold": 0.85
    },
    "thank_you": {
        "text": "Thank you for calling.",
        "file": "common/thank_you.wav",
        "threshold": 0.85
    },
    "anything_else": {
        "text": "Is there anything else I can help you with?",
        "file": "common/anything_else.wav",
        "threshold": 0.8
    },
    "please_rephrase": {
        "text": "Could you please rephrase that?",
        "file": "common/please_rephrase.wav",
        "threshold": 0.85
    },
    "one_moment": {
        "text": "One moment please.",
        "file": "common/one_moment.wav",
        "threshold": 0.85
    },
    "transfer_agent": {
        "text": "Let me connect you to a human agent.",
        "file": "common/transfer_agent.wav",
        "threshold": 0.8
    },
    "goodbye": {
        "text": "Thank you for calling ICICI Lombard Insurance. Have a great day!",
        "file": "common/goodbye.wav",
        "threshold": 0.8
    }
}

# Acknowledgments (very short phrases)
ACKNOWLEDGMENTS = {
    "understand": {
        "text": "I understand.",
        "file": "acknowledgments/understand.wav",
        "threshold": 0.9
    },
    "got_it": {
        "text": "Got it.",
        "file": "acknowledgments/got_it.wav",
        "threshold": 0.9
    },
    "one_moment_ack": {
        "text": "One moment please.",
        "file": "acknowledgments/one_moment.wav",
        "threshold": 0.9
    },
    "checking_ack": {
        "text": "Let me check.",
        "file": "acknowledgments/checking.wav",
        "threshold": 0.9
    }
}


def similarity_ratio(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts"""
    # Normalize texts (lowercase, strip)
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()
    
    return SequenceMatcher(None, t1, t2).ratio()


def get_prerecorded_audio(text: str) -> Optional[str]:
    """
    Check if text matches a pre-recorded response.
    Returns absolute path to audio file if match found, None otherwise.
    
    Args:
        text: The response text to check
        
    Returns:
        Absolute path to audio file or None
    """
    # Check common responses first
    for key, data in COMMON_RESPONSES.items():
        ratio = similarity_ratio(text, data["text"])
        if ratio >= data["threshold"]:
            audio_path = os.path.join(PRERECORDED_DIR, data["file"])
            if os.path.exists(audio_path):
                print(f"✅ Using pre-recorded audio: {key} (similarity: {ratio:.2f})")
                return audio_path
    
    # Check acknowledgments
    for key, data in ACKNOWLEDGMENTS.items():
        ratio = similarity_ratio(text, data["text"])
        if ratio >= data["threshold"]:
            audio_path = os.path.join(PRERECORDED_DIR, data["file"])
            if os.path.exists(audio_path):
                print(f"✅ Using pre-recorded acknowledgment: {key} (similarity: {ratio:.2f})")
                return audio_path
    
    return None


def get_greeting_audio() -> Optional[str]:
    """Get the pre-recorded greeting audio file"""
    audio_path = os.path.join(PRERECORDED_DIR, COMMON_RESPONSES["greeting"]["file"])
    if os.path.exists(audio_path):
        return audio_path
    return None


def get_all_phrases() -> Dict[str, str]:
    """Get all phrases that need pre-recorded audio"""
    phrases = {}
    
    # Add common responses
    for key, data in COMMON_RESPONSES.items():
        phrases[key] = {
            "text": data["text"],
            "file": data["file"]
        }
    
    # Add acknowledgments
    for key, data in ACKNOWLEDGMENTS.items():
        phrases[key] = {
            "text": data["text"],
            "file": data["file"]
        }
    
    return phrases


def is_prerecorded_available(text: str) -> bool:
    """Check if pre-recorded audio is available for this text"""
    return get_prerecorded_audio(text) is not None
