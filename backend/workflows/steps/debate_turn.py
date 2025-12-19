"""
Debate Turn Steps

Handles proposition and opposition debate turns.
"""

import sys
import os
from typing import Dict, Any, Generator, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state import add_message
from tasks import get_debate_task
from utils.state_queries import get_recent_history_formatted
from utils.state_helpers import get_last_message_content
from workflows.config import DebateEvent, DebateEventType
from workflows.steps.initialize import get_agent_by_id


def proposition_turn(
    state: Dict[str, Any],
    stream: bool = True
) -> Generator[DebateEvent, None, Dict[str, Any]]:
    """
    Execute a proposition agent's turn.
    
    Args:
        state: Current debate state
        stream: Whether to stream response
        
    Yields:
        DebateEvent objects for streaming
        
    Returns:
        Updated state dict
    """
    # Get active proposition agent
    active_id = state.get("active_proposition_id")
    agent = get_agent_by_id(active_id)
    
    if not agent:
        raise ValueError(f"Could not find agent with ID: {active_id}")
    
    # Get debate context
    topic = state.get("topic", "")
    recent_history = get_recent_history_formatted(state, n=5)
    
    # Get opponent's last argument
    messages = state.get("messages", [])
    opponent_last = None
    for msg in reversed(messages):
        if msg.get("role") == "opposition":
            opponent_last = msg.get("content")
            break
    
    # Create debate task
    task = get_debate_task(
        topic=topic,
        stance="for",
        debate_history=[
            {"speaker": m.get("agent_name"), "argument": m.get("content")}
            for m in messages[-5:]
        ],
        opponent_last_argument=opponent_last,
        personality_note=agent.personality_type
    )
    
    # Build prompt
    prompt = task.build_prompt()
    
    # Call agent
    try:
        response = agent.run(prompt)
        full_content = response.content if response else ""
        
        # Emit chunks for streaming effect
        if stream and full_content:
            words = full_content.split()
            chunk_size = 5
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                yield DebateEvent(
                    event_type=DebateEventType.AGENT_MESSAGE_CHUNK,
                    data={
                        "agent_id": active_id,
                        "agent_name": agent.name,
                        "role": "proposition",
                        "chunk": chunk,
                    },
                    timestamp=datetime.now().isoformat()
                )
        
        # Emit completion event
        yield DebateEvent(
            event_type=DebateEventType.AGENT_MESSAGE_COMPLETE,
            data={
                "agent_id": active_id,
                "agent_name": agent.name,
                "role": "proposition",
                "content": full_content,
                "word_count": len(full_content.split()) if full_content else 0,
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Update state
        state = add_message(
            state,
            agent_id=active_id,
            agent_name=agent.name,
            role="proposition",
            content=full_content
        )
        
    except Exception as e:
        # Emit error event
        yield DebateEvent(
            event_type=DebateEventType.ERROR,
            data={
                "step": "proposition_turn",
                "error": str(e),
                "agent_id": active_id,
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Use fallback message
        fallback = f"[{agent.name} encountered an error. Continuing with fallback response.]"
        state = add_message(
            state,
            agent_id=active_id,
            agent_name=agent.name,
            role="proposition",
            content=fallback
        )
    
    return state


def opposition_turn(
    state: Dict[str, Any],
    stream: bool = True
) -> Generator[DebateEvent, None, Dict[str, Any]]:
    """
    Execute the opposition agent's turn.
    
    Args:
        state: Current debate state
        stream: Whether to stream response
        
    Yields:
        DebateEvent objects for streaming
        
    Returns:
        Updated state dict
    """
    # Get opposition agent
    opposition_id = state.get("opposition_id")
    agent = get_agent_by_id(opposition_id)
    
    if not agent:
        raise ValueError(f"Could not find opposition agent with ID: {opposition_id}")
    
    # Get debate context
    topic = state.get("topic", "")
    
    # Get proposition's last argument
    messages = state.get("messages", [])
    opponent_last = None
    for msg in reversed(messages):
        if msg.get("role") == "proposition":
            opponent_last = msg.get("content")
            break
    
    # Create debate task
    task = get_debate_task(
        topic=topic,
        stance="against",
        debate_history=[
            {"speaker": m.get("agent_name"), "argument": m.get("content")}
            for m in messages[-5:]
        ],
        opponent_last_argument=opponent_last,
        personality_note=agent.personality_type
    )
    
    # Build prompt
    prompt = task.build_prompt()
    
    # Call agent
    try:
        response = agent.run(prompt)
        full_content = response.content if response else ""
        
        # Emit chunks for streaming effect
        if stream and full_content:
            words = full_content.split()
            chunk_size = 5
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                yield DebateEvent(
                    event_type=DebateEventType.AGENT_MESSAGE_CHUNK,
                    data={
                        "agent_id": opposition_id,
                        "agent_name": agent.name,
                        "role": "opposition",
                        "chunk": chunk,
                    },
                    timestamp=datetime.now().isoformat()
                )
        
        # Emit completion event
        yield DebateEvent(
            event_type=DebateEventType.AGENT_MESSAGE_COMPLETE,
            data={
                "agent_id": opposition_id,
                "agent_name": agent.name,
                "role": "opposition",
                "content": full_content,
                "word_count": len(full_content.split()) if full_content else 0,
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Update state
        state = add_message(
            state,
            agent_id=opposition_id,
            agent_name=agent.name,
            role="opposition",
            content=full_content
        )
        
    except Exception as e:
        # Emit error event
        yield DebateEvent(
            event_type=DebateEventType.ERROR,
            data={
                "step": "opposition_turn",
                "error": str(e),
                "agent_id": opposition_id,
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Use fallback message
        fallback = f"[{agent.name} encountered an error. Continuing with fallback response.]"
        state = add_message(
            state,
            agent_id=opposition_id,
            agent_name=agent.name,
            role="opposition",
            content=fallback
        )
    
    return state


def check_round_completion(state: Dict[str, Any]) -> str:
    """
    Check if a voting round should be triggered.
    
    Args:
        state: Current debate state
        
    Returns:
        "vote" if voting should trigger
        "continue" if debate should continue
        "time_expired" if time is up
    """
    from utils.state_helpers import should_trigger_voting, should_end_debate
    
    # Check time first
    if should_end_debate(state):
        return "time_expired"
    
    # Check if voting should trigger
    if should_trigger_voting(state):
        return "vote"
    
    return "continue"

