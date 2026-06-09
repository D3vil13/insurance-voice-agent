import os
import time
import base64
import logging
import requests
from config import SARVAM_API_KEY, SARVAM_TTS_MODEL, SARVAM_TTS_SPEAKER, SARVAM_TTS_LANGUAGE

logger = logging.getLogger(__name__)

def tts_sarvam(text: str, output_path: str = "output.wav", session_id: str = None, api_key: str = None):
    start_time = time.time()
    key = api_key or SARVAM_API_KEY
    try:
        url = "https://api.sarvam.ai/text-to-speech"
        headers = {
            "api-subscription-key": key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model": SARVAM_TTS_MODEL,
            "target_language_code": SARVAM_TTS_LANGUAGE,
            "speaker": SARVAM_TTS_SPEAKER
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            try:
                err = response.json().get("error", {}).get("message", response.text[:500])
            except Exception:
                err = response.text[:500]
            logger.error(f"[TTS-FAIL] Sarvam API returned {response.status_code}: {err}")
            return {
                "status": "failed",
                "service": "sarvam",
                "output_path": None,
                "error_code": f"HTTP_{response.status_code}",
                "error_message": err
            }

        result = response.json()
        combined = "".join(result["audios"])
        wav_bytes = base64.b64decode(combined)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(wav_bytes)

        elapsed = time.time() - start_time
        logger.info(f"[TTS-SUCCESS] Sarvam AI | Session: {session_id} | "
                    f"Text length: {len(text)} chars | Latency: {elapsed:.2f}s | "
                    f"Output: {output_path}")

        return {
            "status": "success",
            "service": "sarvam",
            "output_path": output_path,
            "latency": elapsed,
            "text_length": len(text),
            "error_code": None
        }

    except Exception as e:
        elapsed = time.time() - start_time
        error_code = type(e).__name__
        logger.error(f"[TTS-FAIL] Sarvam AI | Session: {session_id} | "
                     f"Error: {error_code} - {str(e)}")
        return {
            "status": "failed",
            "service": "sarvam",
            "output_path": None,
            "latency": elapsed,
            "text_length": len(text),
            "error_code": error_code,
            "error_message": str(e)
        }

def tts_with_fallback(text: str, session_id: str = None, segment_id: str = None, api_key: str = None):
    logger.info(f"[TTS-START] Session: {session_id} | Segment: {segment_id}")
    result = tts_sarvam(
        text,
        f"logs/audio_segments/{session_id}_{segment_id}_sarvam.wav",
        session_id,
        api_key=api_key
    )
    if result["status"] == "success":
        return result
    logger.critical(f"[TTS-CRITICAL] Sarvam TTS failed | Session: {session_id}")
    return {
        "status": "failed",
        "service": "all",
        "output_path": None,
        "error_code": "ALL_TTS_FAILED",
        "error_message": result.get("error_message", "Sarvam TTS failed")
    }