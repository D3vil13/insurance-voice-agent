"""
Session Utilities
Audio archiving and session management
"""
import os
import shutil
import logging

# Configure logger
logger = logging.getLogger(__name__)


def archive_session_audio(session_id: str):
    """
    Copy all audio segments for a session to session-specific folder
    
    Args:
        session_id: Session identifier
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        session_audio_dir = f'logs/{session_id}/audio'
        os.makedirs(session_audio_dir, exist_ok=True)
        
        # Copy all audio files for this session
        for filename in os.listdir('logs/audio_segments'):
            if filename.startswith(session_id):
                src = f'logs/audio_segments/{filename}'
                dst = f'{session_audio_dir}/{filename}'
                shutil.copy2(src, dst)
        
        logger.info(f"[ARCHIVE] Audio archived for session: {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"[ARCHIVE-FAIL] Session: {session_id} | Error: {e}")
        return False


def setup_logging():
    """
    Configure logging for voice pipeline
    Creates log directory and sets up file and console handlers
    """
    os.makedirs('logs', exist_ok=True)
    os.makedirs('logs/audio_segments', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/voice_pipeline.log'),
            logging.StreamHandler()
        ]
    )
