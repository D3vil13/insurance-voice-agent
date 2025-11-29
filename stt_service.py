"""
Speech-to-Text (STT) Service with Fallback
Supports Faster-Whisper and Voxtral Mini
"""
import time
import logging
from faster_whisper import WhisperModel

# Configure logger
logger = logging.getLogger(__name__)


def stt_faster_whisper(audio_path: str, session_id: str = None):
    """
    Transcribe audio using Faster-Whisper model
    
    Args:
        audio_path: Path to audio file
        session_id: Session identifier for logging
        
    Returns:
        dict: Result with status, service, transcription, latency, etc.
    """
    start_time = time.time()
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path)
        
        transcription = ""
        segment_count = 0
        for segment in segments:
            transcription += segment.text + " "
            segment_count += 1
        
        elapsed = time.time() - start_time
        
        logger.info(f"[STT-SUCCESS] Faster-Whisper | Session: {session_id} | "
                   f"Segments: {segment_count} | Latency: {elapsed:.2f}s | "
                   f"Length: {len(transcription)} chars")
        
        return {
            'status': 'success',
            'service': 'faster_whisper',
            'transcription': transcription.strip(),
            'latency': elapsed,
            'segment_count': segment_count,
            'error_code': None
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_code = type(e).__name__
        
        logger.error(f"[STT-FAIL] Faster-Whisper | Session: {session_id} | "
                    f"Error: {error_code} - {str(e)} | Latency: {elapsed:.2f}s")
        
        return {
            'status': 'failed',
            'service': 'faster_whisper',
            'transcription': None,
            'latency': elapsed,
            'error_code': error_code,
            'error_message': str(e)
        }


def stt_voxtral_mini(audio_path: str, session_id: str = None):
    """
    Placeholder for Voxtral Mini STT fallback
    
    Args:
        audio_path: Path to audio file
        session_id: Session identifier for logging
        
    Returns:
        dict: Result with status, service, transcription, latency, etc.
    """
    start_time = time.time()
    logger.warning(f"[STT-FALLBACK] Voxtral Mini not implemented | Session: {session_id}")
    elapsed = time.time() - start_time
    
    return {
        'status': 'failed',
        'service': 'voxtral_mini',
        'transcription': None,
        'latency': elapsed,
        'error_code': 'NOT_IMPLEMENTED'
    }


def stt_with_fallback(audio_path: str, session_id: str = None):
    """
    STT with automatic fallback from Faster-Whisper to Voxtral Mini
    
    Args:
        audio_path: Path to audio file
        session_id: Session identifier for logging
        
    Returns:
        dict: Result with status, service, transcription, latency, etc.
    """
    logger.info(f"[STT-START] Session: {session_id} | Audio: {audio_path}")
    
    # Try primary (Faster-Whisper)
    result = stt_faster_whisper(audio_path, session_id)
    
    if result['status'] == 'success':
        return result
    
    # Fallback to Voxtral Mini
    logger.warning(f"[STT-FALLBACK] Switching to Voxtral Mini | Session: {session_id}")
    result = stt_voxtral_mini(audio_path, session_id)
    
    if result['status'] == 'success':
        result['fallback_triggered'] = True
        return result
    
    # Both failed
    logger.critical(f"[STT-CRITICAL] All services failed | Session: {session_id}")
    return {
        'status': 'failed',
        'service': 'all',
        'transcription': None,
        'error_code': 'ALL_STT_FAILED'
    }
