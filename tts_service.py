"""
Text-to-Speech (TTS) Service with Fallback
Supports Google Cloud TTS and Chatterbox local TTS
"""
import os
import time
import logging
import requests
from google.cloud import texttospeech

# Configure logger
logger = logging.getLogger(__name__)


def tts_google_cloud(text: str, output_path: str = 'output_gc.wav', session_id: str = None):
    """
    Generate speech using Google Cloud Text-to-Speech API
    
    Args:
        text: Text to convert to speech
        output_path: Path to save audio file
        session_id: Session identifier for logging
        
    Returns:
        dict: Result with status, service, output_path, latency, etc.
    """
    start_time = time.time()
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16)
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)
        
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        elapsed = time.time() - start_time
        
        # Log success with metrics
        logger.info(f"[TTS-SUCCESS] Google Cloud | Session: {session_id} | "
                   f"Text length: {len(text)} chars | Latency: {elapsed:.2f}s | "
                   f"Output: {output_path}")
        
        return {
            'status': 'success',
            'service': 'google_cloud',
            'output_path': output_path,
            'latency': elapsed,
            'text_length': len(text),
            'error_code': None
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_code = type(e).__name__
        
        logger.error(f"[TTS-FAIL] Google Cloud | Session: {session_id} | "
                    f"Error: {error_code} - {str(e)} | Latency: {elapsed:.2f}s")
        
        return {
            'status': 'failed',
            'service': 'google_cloud',
            'output_path': None,
            'latency': elapsed,
            'text_length': len(text),
            'error_code': error_code,
            'error_message': str(e)
        }


def tts_chatterbox(text: str, output_path: str = 'output_cb.wav', session_id: str = None):
    """
    Generate speech using Chatterbox local TTS service
    
    Args:
        text: Text to convert to speech
        output_path: Path to save audio file
        session_id: Session identifier for logging
        
    Returns:
        dict: Result with status, service, output_path, latency, etc.
    """
    start_time = time.time()
    try:
        api_url = "http://localhost:4123/v1"
        headers = {
            "Authorization": None,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "voice": "en-US-neutral",
            "format": "wav"
        }
        response = requests.post(api_url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        elapsed = time.time() - start_time
        
        logger.info(f"[TTS-SUCCESS] Chatterbox | Session: {session_id} | "
                   f"Text length: {len(text)} chars | Latency: {elapsed:.2f}s | "
                   f"Output: {output_path}")
        
        return {
            'status': 'success',
            'service': 'chatterbox',
            'output_path': output_path,
            'latency': elapsed,
            'text_length': len(text),
            'error_code': None
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_code = type(e).__name__
        
        logger.error(f"[TTS-FAIL] Chatterbox | Session: {session_id} | "
                    f"Error: {error_code} - {str(e)} | Latency: {elapsed:.2f}s")
        
        return {
            'status': 'failed',
            'service': 'chatterbox',
            'output_path': None,
            'latency': elapsed,
            'text_length': len(text),
            'error_code': error_code,
            'error_message': str(e)
        }


def tts_with_fallback(text: str, session_id: str = None, segment_id: str = None):
    """
    TTS with automatic fallback from Google Cloud to Chatterbox
    
    Args:
        text: Text to convert to speech
        session_id: Session identifier for logging
        segment_id: Segment identifier for file naming
        
    Returns:
        dict: Result with status, service, output_path, latency, etc.
    """
    logger.info(f"[TTS-START] Session: {session_id} | Segment: {segment_id}")
    
    # Try primary (Google Cloud)
    result = tts_google_cloud(text, f'logs/audio_segments/{session_id}_{segment_id}_gc.wav', session_id)
    
    if result['status'] == 'success':
        return result
    
    # Fallback to Chatterbox
    logger.warning(f"[TTS-FALLBACK] Switching to Chatterbox | Session: {session_id}")
    result = tts_chatterbox(text, f'logs/audio_segments/{session_id}_{segment_id}_cb.wav', session_id)
    
    if result['status'] == 'success':
        result['fallback_triggered'] = True
        return result
    
    # Both failed
    logger.critical(f"[TTS-CRITICAL] All services failed | Session: {session_id}")
    return {
        'status': 'failed',
        'service': 'all',
        'output_path': None,
        'error_code': 'ALL_TTS_FAILED'
    }
