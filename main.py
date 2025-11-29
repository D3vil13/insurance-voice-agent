#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Entry Point for LangGraph Voice Agent
Run this file to start the interactive voice call system
"""
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from state import create_initial_state
from graph import build_graph
from config import MAX_TURNS


def check_dependencies():
    """Check if all required dependencies are available"""
    dependencies_ok = True
    
    # Check voice pipeline
    try:
        from tts_service import tts_with_fallback
        from stt_service import stt_with_fallback
        print("  Voice Pipeline: ✓ Available")
    except ImportError:
        print("  Voice Pipeline: ❌ Not available")
        dependencies_ok = False
    
    # Check RAG
    try:
        import chromadb
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("  RAG & LLM: ✓ Available")
    except ImportError:
        print("  RAG & LLM: ❌ Not available")
        dependencies_ok = False
    
    # Check LangGraph
    try:
        from langgraph.graph import StateGraph
        print("  LangGraph: ✓ Available")
    except ImportError:
        print("  LangGraph: ❌ Not available")
        dependencies_ok = False
    
    return dependencies_ok


def main():
    """Main execution function"""
    print("""
    ============================================================
         INSURANCE AI VOICE AGENT - LANGGRAPH VERSION           
    ============================================================
    """)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Missing required dependencies. Exiting.")
        print("\nInstall with: pip install langgraph chromadb sentence-transformers faster-whisper google-cloud-texttospeech sounddevice soundfile")
        sys.exit(1)
    
    # Build graph
    print("\n🔧 Building LangGraph workflow...")
    try:
        graph = build_graph()
        print("✓ Graph compiled successfully!")
    except Exception as e:
        print(f"❌ Failed to build graph: {e}")
        sys.exit(1)
    
    # Initialize state
    initial_state = create_initial_state(max_turns=MAX_TURNS)
    
    print("\n" + "="*60)
    print("INTERACTIVE VOICE CALL - LangGraph Mode")
    print("="*60)
    print("• Speak naturally after the agent finishes")
    print("• The system will auto-detect when you stop speaking")
    print("• Press Ctrl+C to end call")
    print("="*60)
    
    try:
        # Execute graph
        print("\n🚀 Starting LangGraph execution...")
        result = graph.invoke(initial_state)
        
        print("\n✓ LangGraph execution completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Call interrupted by user")
        print("Session data may be incomplete.")
    except Exception as e:
        print(f"\n❌ Error during call: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
