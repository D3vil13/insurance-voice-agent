#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Backend for Insurance Voice Agent
Provides REST API endpoints for web frontend
"""
import sys
import io
import os
import tempfile
from datetime import datetime
from typing import Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Import existing modules
from utils import semantic_search, generate_answer_with_llm
from stt_service import stt_with_fallback
from tts_service import tts_with_fallback

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Voice Agent API",
    description="AI-powered insurance assistant with voice capabilities",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
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

# Create audio output directory
os.makedirs('api_audio_output', exist_ok=True)


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
async def process_audio(audio: UploadFile = File(...)):
    """
    Process audio file: STT → RAG → LLM → TTS
    
    Args:
        audio: Audio file from frontend (WAV format recommended)
    
    Returns:
        JSON with user_text, agent_response, and audio_url
    """
    temp_path = None
    output_path = None
    
    try:
        # Generate session ID
        session_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_path = temp_audio.name
        
        print(f"[API] Processing audio for session: {session_id}")
        
        # Step 1: Speech-to-Text
        print("[API] Running STT...")
        stt_result = stt_with_fallback(temp_path, session_id=session_id)
        
        if stt_result['status'] != 'success':
            raise HTTPException(
                status_code=500, 
                detail=f"Speech-to-text failed: {stt_result.get('error_message', 'Unknown error')}"
            )
        
        user_text = stt_result['transcription']
        print(f"[API] User said: {user_text}")
        
        # Step 2: RAG Search
        print("[API] Searching knowledge base...")
        hits = semantic_search(user_text)
        retrieved_docs = [hit["doc"] for hit in hits]
        
        # Step 3: LLM Response Generation
        print("[API] Generating response...")
        if retrieved_docs:
            agent_response = generate_answer_with_llm(user_text, retrieved_docs)
        else:
            agent_response = "I apologize, I couldn't find relevant information about that. Could you please rephrase your question?"
        
        print(f"[API] Agent response: {agent_response}")
        
        # Step 4: Text-to-Speech
        print("[API] Converting to speech...")
        tts_result = tts_with_fallback(
            agent_response, 
            session_id=session_id, 
            segment_id="response"
        )
        
        if tts_result['status'] != 'success':
            # Return text response even if TTS fails
            return JSONResponse({
                "user_text": user_text,
                "agent_response": agent_response,
                "audio_url": None,
                "warning": "TTS failed, text-only response"
            })
        
        output_path = tts_result['output_path']
        
        # Copy audio to API output directory for serving
        api_audio_filename = f"{session_id}_response.wav"
        api_audio_path = os.path.join('api_audio_output', api_audio_filename)
        
        import shutil
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
        # Clean up temp file
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
    """
    Serve audio files
    
    Args:
        filename: Audio file name
    
    Returns:
        Audio file
    """
    file_path = os.path.join('api_audio_output', filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path, 
        media_type="audio/wav",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        import chromadb
        from config import CHROMA_DB_PATH, OPENROUTER_API_KEY
        
        # Check database
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(name="insurance_docs")
        doc_count = collection.count()
        
        # Check API key
        api_key_status = "configured" if OPENROUTER_API_KEY else "missing"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": "connected",
                    "path": CHROMA_DB_PATH,
                    "documents": doc_count
                },
                "api_key": {
                    "status": api_key_status
                },
                "services": {
                    "stt": "available",
                    "tts": "available",
                    "llm": "available"
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
async def start_call():
    """
    Initialize a new call session with greeting
    
    Returns:
        JSON with session_id, greeting_text, and greeting_audio_url
    """
    try:
        # Generate session ID
        session_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Greeting message (same as in nodes.py)
        greeting = "Hi, this is PolicyPal AI from ICICI Lombard Insurance. How can I help you today?"
        
        print(f"[API] Starting new call session: {session_id}")
        
        # Generate greeting audio
        tts_result = tts_with_fallback(
            greeting,
            session_id=session_id,
            segment_id="greeting"
        )
        
        if tts_result['status'] != 'success':
            # Return text-only greeting if TTS fails
            return JSONResponse({
                "session_id": session_id,
                "greeting_text": greeting,
                "greeting_audio_url": None,
                "warning": "TTS failed, text-only greeting"
            })
        
        # Copy audio to API output directory
        greeting_filename = f"{session_id}_greeting.wav"
        greeting_path = os.path.join('api_audio_output', greeting_filename)
        
        import shutil
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
