"""
LangGraph Construction and Routing Logic
Builds the conversation workflow graph
"""
from typing import Literal
from langgraph.graph import StateGraph, START, END

from state import AgentState
from nodes import (
    initialize_session,
    greet_user,
    listen_to_user,
    detect_intent,
    retrieve_information,
    generate_response,
    check_continue,
    end_call
)


# ========== ROUTING FUNCTIONS ==========

def should_continue_conversation(state: AgentState) -> Literal["continue", "end"]:
    """Router: Decide whether to continue or end conversation"""
    if state.get('should_end', False):
        return "end"
    return "continue"


# ========== GRAPH BUILDER ==========

def build_graph():
    """Build and compile the LangGraph workflow"""
    
    # Create graph builder
    graph_builder = StateGraph(AgentState)
    
    # Add nodes
    graph_builder.add_node("initialize_session", initialize_session)
    graph_builder.add_node("greet_user", greet_user)
    graph_builder.add_node("listen_to_user", listen_to_user)
    graph_builder.add_node("detect_intent", detect_intent)
    graph_builder.add_node("retrieve_information", retrieve_information)
    graph_builder.add_node("generate_response", generate_response)
    graph_builder.add_node("check_continue", check_continue)
    graph_builder.add_node("end_call", end_call)
    
    # Add edges
    graph_builder.add_edge(START, "initialize_session")
    graph_builder.add_edge("initialize_session", "greet_user")
    graph_builder.add_edge("greet_user", "listen_to_user")
    graph_builder.add_edge("listen_to_user", "detect_intent")
    graph_builder.add_edge("detect_intent", "retrieve_information")
    graph_builder.add_edge("retrieve_information", "generate_response")
    graph_builder.add_edge("generate_response", "check_continue")
    
    # Add conditional edge
    graph_builder.add_conditional_edges(
        "check_continue",
        should_continue_conversation,
        {
            "continue": "listen_to_user",
            "end": "end_call"
        }
    )
    
    graph_builder.add_edge("end_call", END)
    
    # Compile graph
    graph = graph_builder.compile()
    
    return graph
