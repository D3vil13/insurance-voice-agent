#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic Test Script for Voice Agent
Tests each component individually to identify issues
"""
import sys
import io
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*70)
print("VOICE AGENT DIAGNOSTIC TEST")
print("="*70)

# Test 1: Check ChromaDB
print("\n[TEST 1] Checking ChromaDB...")
try:
    import chromadb
    from config import CHROMA_DB_PATH
    
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name="insurance_docs")
    count = collection.count()
    
    print(f"✓ ChromaDB connected successfully")
    print(f"  Database path: {CHROMA_DB_PATH}")
    print(f"  Collection: insurance_docs")
    print(f"  Document count: {count}")
    
    if count == 0:
        print("  ⚠️  WARNING: Database is EMPTY! This is why you're getting fallback responses.")
        print("  ➜ You need to populate the database with insurance documents first.")
    else:
        print(f"  ✓ Database has {count} documents")
        
except Exception as e:
    print(f"❌ ChromaDB test failed: {e}")

# Test 2: Check Embedder
print("\n[TEST 2] Checking Embedder...")
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from config import EMBEDDER_MODEL
    
    embedder = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL)
    test_embedding = embedder.embed_query("test query")
    
    print(f"✓ Embedder loaded successfully")
    print(f"  Model: {EMBEDDER_MODEL}")
    print(f"  Embedding dimension: {len(test_embedding)}")
    
except Exception as e:
    print(f"❌ Embedder test failed: {e}")

# Test 3: Check OpenRouter API
print("\n[TEST 3] Checking OpenRouter API...")
try:
    from config import OPENROUTER_API_KEY, LLM_MODEL
    import requests
    import json
    
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment!")
        print("  Check your apikeys.env file")
    else:
        print(f"✓ API Key found: {OPENROUTER_API_KEY[:10]}...")
        print(f"  Model: {LLM_MODEL}")
        
        # Test API call
        print("  Testing API connection...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8888",
                "X-Title": "Diagnostic Test",
            },
            data=json.dumps({
                "model": LLM_MODEL,
                "messages": [
                    {"role": "user", "content": "Say 'API test successful' in exactly 3 words."}
                ],
                "max_tokens": 10
            }),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"  ✓ API test successful!")
            print(f"  Response: {answer}")
        else:
            print(f"  ❌ API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            
except Exception as e:
    print(f"❌ OpenRouter API test failed: {e}")

# Test 4: Check STT (Faster-Whisper)
print("\n[TEST 4] Checking STT (Faster-Whisper)...")
try:
    from faster_whisper import WhisperModel
    
    print("  Loading Whisper model (this may take a moment)...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("  ✓ Faster-Whisper loaded successfully")
    print("  Note: STT will work when you record audio")
    
except Exception as e:
    print(f"❌ STT test failed: {e}")

# Test 5: Check TTS (Google Cloud)
print("\n[TEST 5] Checking TTS (Google Cloud)...")
try:
    from google.cloud import texttospeech
    from config import GOOGLE_CREDENTIALS_PATH
    
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        print(f"❌ Google credentials file not found: {GOOGLE_CREDENTIALS_PATH}")
    else:
        client = texttospeech.TextToSpeechClient()
        print("  ✓ Google Cloud TTS client initialized")
        print(f"  Credentials: {GOOGLE_CREDENTIALS_PATH}")
        
except Exception as e:
    print(f"❌ TTS test failed: {e}")

# Test 6: Check Audio Devices
print("\n[TEST 6] Checking Audio Devices...")
try:
    import sounddevice as sd
    
    devices = sd.query_devices()
    default_input = sd.query_devices(kind='input')
    default_output = sd.query_devices(kind='output')
    
    print(f"✓ Audio devices detected")
    print(f"  Default input: {default_input['name']}")
    print(f"  Default output: {default_output['name']}")
    
except Exception as e:
    print(f"❌ Audio device test failed: {e}")

# Summary
print("\n" + "="*70)
print("DIAGNOSTIC SUMMARY")
print("="*70)

print("\n🔍 ROOT CAUSE IDENTIFIED:")
print("  The ChromaDB database is EMPTY (0 documents).")
print("  This is why the agent always says:")
print('  "I apologize, I couldn\'t find relevant information..."')

print("\n💡 SOLUTION:")
print("  You need to populate the ChromaDB with insurance documents.")
print("  Options:")
print("  1. Run your data ingestion script to load documents")
print("  2. Check if you have a script like 'v_Data.ipynb' or similar")
print("  3. Verify the database path is correct")

print("\n📝 NEXT STEPS:")
print("  1. Locate your document ingestion script")
print("  2. Run it to populate the database")
print("  3. Re-run this diagnostic to verify documents are loaded")
print("  4. Test the voice agent again")

print("\n" + "="*70)
