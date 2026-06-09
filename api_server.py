#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Backend for Insurance Voice Agent
Provides REST API endpoints for web frontend
"""
import os
import tempfile
import shutil
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from utils import semantic_search, generate_answer_with_llm
from stt_service import stt_with_fallback
from tts_service import tts_with_fallback
from config import SARVAM_API_KEY

# Use /tmp for ephemeral storage on production (Render/Vercel)
AUDIO_OUTPUT_DIR = os.environ.get("AUDIO_OUTPUT_DIR", "api_audio_output")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Voice Agent API",
    description="AI-powered insurance assistant with voice capabilities",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TextQuery(BaseModel):
    text: str
    session_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_docs: int


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    try:
        # Import here to avoid circular imports
        import chromadb
        from config import CHROMA_DB_PATH
        
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(name="insurance_docs")
        doc_count = collection.count()
        
        return HealthResponse(
            status="Insurance Voice Agent API is running",
            timestamp=datetime.now().isoformat(),
            database_docs=doc_count
        )
    except Exception as e:
        return HealthResponse(
            status=f"Running with errors: {str(e)}",
            timestamp=datetime.now().isoformat(),
            database_docs=0
        )


@app.post("/api/process-audio")
async def process_audio(
    audio: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    temp_path = None
    output_path = None
    sarvam_key = x_api_key or SARVAM_API_KEY
    
    try:
        session_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        orig_filename = audio.filename or "recording.webm"
        orig_content_type = audio.content_type or "audio/webm"
        ext = os.path.splitext(orig_filename)[1] or ".webm"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_path = temp_audio.name
        
        print(f"[API] Processing audio for session: {session_id} (type={orig_content_type})")
        
        print("[API] Running STT...")
        stt_result = stt_with_fallback(temp_path, session_id=session_id, api_key=sarvam_key, content_type=orig_content_type)
        
        if stt_result['status'] != 'success':
            raise HTTPException(
                status_code=500, 
                detail=f"Speech-to-text failed: {stt_result.get('error_message', 'Unknown error')}"
            )
        
        user_text = stt_result['transcription']
        print(f"[API] User said: {user_text}")
        
        print("[API] Searching knowledge base...")
        hits = semantic_search(user_text)
        retrieved_docs = [hit["doc"] for hit in hits]
        
        print("[API] Generating response...")
        if retrieved_docs:
            agent_response = generate_answer_with_llm(user_text, retrieved_docs)
        else:
            agent_response = "I apologize, I couldn't find relevant information about that. Could you please rephrase your question?"
        
        print(f"[API] Agent response: {agent_response}")
        
        print("[API] Converting to speech...")
        tts_result = tts_with_fallback(
            agent_response, 
            session_id=session_id, 
            segment_id="response",
            api_key=sarvam_key
        )
        
        if tts_result['status'] != 'success':
            return JSONResponse({
                "user_text": user_text,
                "agent_response": agent_response,
                "audio_url": None,
                "warning": "TTS failed, text-only response"
            })
        
        output_path = tts_result['output_path']
        
        api_audio_filename = f"{session_id}_response.wav"
        api_audio_path = os.path.join(AUDIO_OUTPUT_DIR, api_audio_filename)
        
        shutil.copy2(output_path, api_audio_path)
        
        print(f"[API] Success! Audio saved to: {api_audio_path}")
        
        return JSONResponse({
            "user_text": user_text,
            "agent_response": agent_response,
            "audio_url": f"/api/audio/{api_audio_filename}",
            "sources_found": len(retrieved_docs)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


@app.post("/api/text-query")
async def text_query(query: TextQuery):
    """
    Process text query: RAG → LLM
    
    Args:
        query: TextQuery object with text and optional session_id
    
    Returns:
        JSON with user_text, agent_response, and sources count
    """
    try:
        user_text = query.text.strip()
        session_id = query.session_id or f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not user_text:
            raise HTTPException(status_code=400, detail="Text query cannot be empty")
        
        print(f"[API] Text query from session {session_id}: {user_text}")
        
        # RAG Search
        print("[API] Searching knowledge base...")
        hits = semantic_search(user_text)
        retrieved_docs = [hit["doc"] for hit in hits]
        
        # LLM Response
        print("[API] Generating response...")
        if retrieved_docs:
            agent_response = generate_answer_with_llm(user_text, retrieved_docs)
        else:
            agent_response = "I apologize, I couldn't find relevant information about that. Could you please rephrase your question?"
        
        print(f"[API] Agent response: {agent_response}")
        
        return JSONResponse({
            "user_text": user_text,
            "agent_response": agent_response,
            "sources_found": len(retrieved_docs),
            "session_id": session_id
        })
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        file_path, 
        media_type="audio/wav",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@app.get("/health")
async def health_check():
    try:
        import chromadb
        from config import CHROMA_DB_PATH, OPENROUTER_API_KEY, SARVAM_API_KEY
        
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(name="insurance_docs")
        doc_count = collection.count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": "connected",
                    "path": CHROMA_DB_PATH,
                    "documents": doc_count
                },
                "api_keys": {
                    "openrouter": "configured" if OPENROUTER_API_KEY else "missing",
                    "sarvam": "configured" if SARVAM_API_KEY else "missing"
                },
                "services": {
                    "stt": "sarvam_ai",
                    "tts": "sarvam_ai",
                    "llm": "openrouter"
                }
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/start-call")
async def start_call(x_api_key: Optional[str] = Header(None)):
    sarvam_key = x_api_key or SARVAM_API_KEY
    try:
        session_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        greeting = "Hi, this is PolicyPal AI from ICICI Lombard Insurance. How can I help you today?"
        
        print(f"[API] Starting new call session: {session_id}")
        
        tts_result = tts_with_fallback(
            greeting,
            session_id=session_id,
            segment_id="greeting",
            api_key=sarvam_key
        )
        
        if tts_result['status'] != 'success':
            return JSONResponse({
                "session_id": session_id,
                "greeting_text": greeting,
                "greeting_audio_url": None,
                "warning": "TTS failed, text-only greeting"
            })
        
        greeting_filename = f"{session_id}_greeting.wav"
        greeting_path = os.path.join(AUDIO_OUTPUT_DIR, greeting_filename)
        shutil.copy2(tts_result['output_path'], greeting_path)
        
        print(f"[API] Call started successfully: {session_id}")
        
        return JSONResponse({
            "session_id": session_id,
            "greeting_text": greeting,
            "greeting_audio_url": f"/api/audio/{greeting_filename}"
        })
        
    except Exception as e:
        print(f"[API] Error starting call: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debug/voice")
async def debug_voice(x_api_key: Optional[str] = Header(None), api_key: Optional[str] = None):
    sarvam_key = x_api_key or api_key or SARVAM_API_KEY
    results = {"tts": None, "stt": None, "errors": []}

    # Test TTS
    try:
        tts_result = tts_with_fallback("Hello, this is a test.", session_id="debug", segment_id="test", api_key=sarvam_key)
        results["tts"] = {
            "status": tts_result["status"],
            "service": tts_result.get("service"),
            "error": tts_result.get("error_message") if tts_result["status"] != "success" else None
        }
        if tts_result["status"] == "success" and os.path.exists(tts_result["output_path"]):
            os.unlink(tts_result["output_path"])
    except Exception as e:
        results["tts"] = {"status": "failed", "error": str(e)}

    # Test STT by generating a test tone file
    try:
        import wave, struct, math
        test_wav = os.path.join(tempfile.gettempdir(), "debug_test.wav")
        with wave.open(test_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            for i in range(16000):
                val = int(math.sin(2 * math.pi * 440 * i / 16000) * 8000)
                wf.writeframes(struct.pack("<h", val))
        stt_result = stt_with_fallback(test_wav, session_id="debug", api_key=sarvam_key)
        results["stt"] = {
            "status": stt_result["status"],
            "service": stt_result.get("service"),
            "error": stt_result.get("error_message") if stt_result["status"] != "success" else None
        }
        os.unlink(test_wav)
    except Exception as e:
        results["stt"] = {"status": "failed", "error": str(e)}

    return results


@app.post("/api/validate-key")
async def validate_sarvam_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        return JSONResponse({"valid": False, "error": "No API key provided"}, status_code=400)
    try:
        import requests as http
        resp = http.post(
            "https://api.sarvam.ai/text-to-speech",
            headers={"api-subscription-key": x_api_key, "Content-Type": "application/json"},
            json={"text": "Hi", "model": "bulbul:v3", "target_language_code": "en-IN", "speaker": "shubh"},
            timeout=10
        )
        if resp.status_code == 200:
            return {"valid": True}
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:200])
        except Exception:
            msg = resp.text[:200]
        return JSONResponse({"valid": False, "error": msg, "code": resp.status_code})
    except Exception as e:
        return JSONResponse({"valid": False, "error": str(e)})


if __name__ == "__main__":
    print("="*70)
    print("INSURANCE VOICE AGENT API SERVER")
    print("="*70)
    print("\n🚀 Starting server on http://0.0.0.0:8000")
    print("📖 API docs available at http://0.0.0.0:8000/docs")
    print("🏥 Health check at http://0.0.0.0:8000/health")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
