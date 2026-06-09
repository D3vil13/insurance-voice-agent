import time
import logging
import requests
from config import SARVAM_API_KEY, SARVAM_STT_MODEL

logger = logging.getLogger(__name__)

def stt_sarvam(audio_path: str, session_id: str = None, api_key: str = None):
    start_time = time.time()
    key = api_key or SARVAM_API_KEY
    try:
        url = "https://api.sarvam.ai/speech-to-text"
        headers = {"api-subscription-key": key}
        with open(audio_path, "rb") as f:
            files = {"file": ("audio.wav", f, "audio/wav")}
            data = {"model": SARVAM_STT_MODEL, "mode": "transcribe"}
            response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code != 200:
            err = response.json().get("error", {}).get("message", response.text)
            return {
                "status": "failed",
                "service": "sarvam",
                "transcription": None,
                "error_code": f"HTTP_{response.status_code}",
                "error_message": err
            }

        result = response.json()
        transcription = result.get("transcript", "").strip()
        elapsed = time.time() - start_time

        logger.info(f"[STT-SUCCESS] Sarvam AI | Session: {session_id} | "
                    f"Latency: {elapsed:.2f}s | Length: {len(transcription)} chars")

        return {
            "status": "success",
            "service": "sarvam",
            "transcription": transcription,
            "latency": elapsed,
            "segment_count": 1,
            "error_code": None
        }

    except Exception as e:
        elapsed = time.time() - start_time
        error_code = type(e).__name__
        logger.error(f"[STT-FAIL] Sarvam AI | Session: {session_id} | "
                     f"Error: {error_code} - {str(e)}")
        return {
            "status": "failed",
            "service": "sarvam",
            "transcription": None,
            "latency": elapsed,
            "error_code": error_code,
            "error_message": str(e)
        }

def stt_with_fallback(audio_path: str, session_id: str = None, api_key: str = None):
    logger.info(f"[STT-START] Session: {session_id} | Audio: {audio_path}")
    result = stt_sarvam(audio_path, session_id, api_key=api_key)
    if result["status"] == "success":
        return result
    return {
        "status": "failed",
        "service": "all",
        "transcription": None,
        "error_code": "ALL_STT_FAILED",
        "error_message": result.get("error_message", "Sarvam STT failed")
    }