"""
LangGraph Node Functions for Voice Agent
Each node represents a step in the conversation workflow
"""
import os
import time
import soundfile as sf
from datetime import datetime

from state import AgentState
from utils import (
    semantic_search,
    generate_answer_with_llm,
    record_with_silence_detection,
    play_audio
)
from tts_service import tts_with_fallback
from stt_service import stt_with_fallback
from session_utils import archive_session_audio
from config import MAX_RECORDING_DURATION, SILENCE_DURATION, SAMPLE_RATE


# ========== NODE FUNCTIONS ==========

def initialize_session(state: AgentState) -> AgentState:
    """Node: Initialize a new call session"""
    print("\n" + "="*60)
    print("🚀 INITIALIZING CALL SESSION")
    print("="*60)
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().isoformat()
    
    # Create directories
    os.makedirs('logs/audio_segments', exist_ok=True)
    os.makedirs(f'logs/{session_id}', exist_ok=True)
    
    # Initialize state
    state['session_id'] = session_id
    state['timestamp'] = timestamp
    state['current_turn'] = 0
    state['should_end'] = False
    
    print(f"✓ Session ID: {session_id}")
    print(f"✓ Timestamp: {timestamp}")
    
    return state


def greet_user(state: AgentState) -> AgentState:
    """Node: Greet the user and start conversation"""
    print("\n" + "="*60)
    print("👋 GREETING USER")
    print("="*60)
    
    greeting = "Hi, this is PolicyPal AI from ICICI Lombard Insurance. How can I help you today?"
    print(f"\n🤖 Agent: {greeting}")
    
    state['transcript'].append(f"Agent: {greeting}")
    
    # Generate TTS
    tts_result = tts_with_fallback(
        greeting,
        session_id=state['session_id'],
        segment_id="greeting"
    )
    
    if tts_result['status'] == 'success':
        play_audio(tts_result['output_path'])
        state['agent_audio_path'] = tts_result['output_path']
    
    return state


def listen_to_user(state: AgentState) -> AgentState:
    """Node: Record and transcribe user speech"""
    state['current_turn'] += 1
    turn = state['current_turn']
    
    print(f"\n{'='*60}")
    print(f"TURN {turn}")
    print("="*60)
    
    # Wait a moment before listening
    time.sleep(1)
    
    # Record user with automatic silence detection
    audio_data = record_with_silence_detection(
        max_duration=MAX_RECORDING_DURATION,
        silence_duration=SILENCE_DURATION
    )
    
    # Save audio file
    audio_file = f"logs/audio_segments/{state['session_id']}_user_turn_{turn}.wav"
    sf.write(audio_file, audio_data, SAMPLE_RATE)
    print(f"✓ Recording saved: {audio_file}")
    
    state['user_audio_path'] = audio_file
    
    # Transcribe user input
    print("\n📝 Transcribing your speech...")
    stt_result = stt_with_fallback(audio_file, state['session_id'])
    
    if stt_result['status'] != 'success':
        print("❌ Could not transcribe audio")
        state['transcript'].append("User: [transcription failed]")
        return state
    
    user_text = stt_result['transcription']
    print(f"\n👤 You said: {user_text}")
    
    state['transcript'].append(f"User: {user_text}")
    state['memory']['last_user_message'] = user_text
    
    # Track STT metrics
    state['voice_metrics']['stt_calls'].append({
        'turn': turn,
        'service': stt_result.get('service'),
        'status': stt_result.get('status'),
        'latency': stt_result.get('latency', 0),
        'segment_count': stt_result.get('segment_count', 0)
    })
    state['voice_metrics']['total_stt_latency'] += stt_result.get('latency', 0)
    
    return state


def detect_intent(state: AgentState) -> AgentState:
    """Node: Detect user intent from their message"""
    user_text = state['memory'].get('last_user_message', '').lower()
    
    print("\n🎯 Detecting intent...")
    
    # Check for end-of-call keywords
    if any(word in user_text for word in ["goodbye", "bye", "thank you bye", "that's all", "nothing else"]):
        state['intent'] = "end_call"
        state['should_end'] = True
        print("✓ Intent: END CALL")
        return state
    
    # Detect intent using keywords
    if any(kw in user_text for kw in ["claim", "accident", "damage", "incident", "file", "report", "theft", "stolen"]):
        state['intent'] = "claims"
    elif any(kw in user_text for kw in ["policy", "quote", "coverage", "complaint", "help", "service", "question", "premium", "renew"]):
        state['intent'] = "customer_service"
    else:
        state['intent'] = "general"
    
    print(f"✓ Intent detected: {state['intent']}")
    
    return state


def retrieve_information(state: AgentState) -> AgentState:
    """Node: Retrieve relevant information from ChromaDB"""
    user_query = state['memory'].get('last_user_message', '')
    
    if not user_query:
        print("⚠️  No user query to search")
        state['retrieved_info'] = []
        return state
    
    print("\n🔍 Searching knowledge base...")
    print(f"  Query: '{user_query}'")
    
    try:
        hits = semantic_search(user_query)
        state['retrieved_info'] = [hit["doc"] for hit in hits]
        
        print(f"✓ Retrieved {len(state['retrieved_info'])} relevant documents")
        
        # Debug: Show retrieved content (truncated)
        if state['retrieved_info']:
            for i, doc in enumerate(state['retrieved_info'][:2], 1):
                preview = doc[:150] + "..." if len(doc) > 150 else doc
                print(f"  Doc {i}: {preview}")
        else:
            print("  ⚠️  WARNING: No documents found in database!")
            print("  ➜ This means ChromaDB is empty or query didn't match any docs")
            
    except Exception as e:
        print(f"❌ RAG retrieval error: {e}")
        import traceback
        traceback.print_exc()
        state['retrieved_info'] = []
    
    return state


def generate_response(state: AgentState) -> AgentState:
    """Node: Generate LLM response and convert to speech"""
    user_query = state['memory'].get('last_user_message', '')
    retrieved_docs = state['retrieved_info']
    
    print("\n🤖 Generating response...")
    print(f"  Retrieved docs count: {len(retrieved_docs)}")
    
    # Generate response using LLM
    if retrieved_docs:
        print("  ✓ Using LLM with retrieved context")
        agent_response = generate_answer_with_llm(user_query, retrieved_docs)
    else:
        print("  ⚠️  No documents retrieved - using fallback message")
        print("  ➜ This is why you're seeing the generic response!")
        print("  ➜ Solution: Populate ChromaDB with insurance documents")
        agent_response = "I apologize, I couldn't find relevant information. Could you please rephrase your question?"
    
    print(f"\n🤖 Agent: {agent_response}")
    state['transcript'].append(f"Agent: {agent_response}")
    
    # Convert to speech
    print("\n🎵 Converting to speech...")
    tts_result = tts_with_fallback(
        agent_response,
        session_id=state['session_id'],
        segment_id=f"turn_{state['current_turn']}"
    )
    
    # Track TTS metrics
    state['voice_metrics']['tts_calls'].append({
        'turn': state['current_turn'],
        'service': tts_result.get('service'),
        'status': tts_result.get('status'),
        'latency': tts_result.get('latency', 0),
        'text_length': tts_result.get('text_length', 0),
        'fallback_triggered': tts_result.get('fallback_triggered', False)
    })
    state['voice_metrics']['total_tts_latency'] += tts_result.get('latency', 0)
    
    if tts_result.get('fallback_triggered'):
        state['voice_metrics']['fallback_count'] += 1
    
    # Play audio
    if tts_result['status'] == 'success':
        play_audio(tts_result['output_path'])
        state['agent_audio_path'] = tts_result['output_path']
    else:
        print("❌ Could not generate speech")
    
    return state


def check_continue(state: AgentState) -> AgentState:
    """Node: Check if conversation should continue"""
    # Check if max turns reached
    if state['current_turn'] >= state['max_turns']:
        print(f"\n⚠️  Maximum turns ({state['max_turns']}) reached")
        state['should_end'] = True
    
    return state


def end_call(state: AgentState) -> AgentState:
    """Node: End the call gracefully"""
    print("\n" + "="*60)
    print("👋 ENDING CALL")
    print("="*60)
    
    farewell = "Thank you for calling ICICI Lombard Insurance. Have a great day!"
    print(f"\n🤖 Agent: {farewell}")
    state['transcript'].append(f"Agent: {farewell}")
    
    # TTS for farewell
    tts_result = tts_with_fallback(
        farewell,
        session_id=state['session_id'],
        segment_id="farewell"
    )
    
    if tts_result['status'] == 'success':
        play_audio(tts_result['output_path'])
    
    # Archive audio segments
    archive_session_audio(state['session_id'])
    
    # Save transcript
    transcript_path = f"logs/{state['session_id']}/transcript.txt"
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(f"Session ID: {state['session_id']}\n")
        f.write(f"Intent: {state.get('intent', 'N/A')}\n")
        f.write(f"Turns: {state['current_turn']}\n")
        f.write("="*60 + "\n\n")
        f.write("\n".join(state['transcript']))
    
    print(f"\n✓ Call ended. Session ID: {state['session_id']}")
    print(f"📁 Logs saved to: logs/{state['session_id']}/")
    
    # Print summary
    print("\n" + "="*60)
    print("CALL SUMMARY")
    print("="*60)
    print(f"Turns: {state['current_turn']}")
    print(f"Intent: {state.get('intent', 'N/A')}")
    print(f"\nFull transcript:")
    for line in state['transcript']:
        print(f"  {line}")
    
    return state
