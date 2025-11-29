"""
State Definition for LangGraph Voice Agent
"""
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """LangGraph state for voice call agent"""
    session_id: str
    transcript: Annotated[List[str], add_messages]
    intent: Optional[str]
    memory: Dict[str, Any]
    retrieved_info: List[str]
    timestamp: str
    voice_metrics: Dict[str, Any]
    current_turn: int
    user_audio_path: Optional[str]
    agent_audio_path: Optional[str]
    should_end: bool
    max_turns: int


def create_initial_state(max_turns: int = 5) -> AgentState:
    """Create initial state for a new conversation"""
    return {
        "session_id": "",
        "transcript": [],
        "intent": None,
        "memory": {},
        "retrieved_info": [],
        "timestamp": "",
        "voice_metrics": {
            'tts_calls': [],
            'stt_calls': [],
            'total_tts_latency': 0.0,
            'total_stt_latency': 0.0,
            'fallback_count': 0,
            'errors': []
        },
        "current_turn": 0,
        "user_audio_path": None,
        "agent_audio_path": None,
        "should_end": False,
        "max_turns": max_turns
    }
