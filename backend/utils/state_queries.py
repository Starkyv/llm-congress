"""
State Query Functions

Functions to query and extract data from debate state.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


def get_recent_history(state: Dict, n: int = 5) -> List[Dict]:
    """
    Get the last N messages from debate history.
    
    Args:
        state: Current state dict
        n: Number of messages to retrieve
        
    Returns:
        List of recent message dicts
    """
    messages = state.get("messages", [])
    return messages[-n:] if len(messages) > n else messages


def get_recent_history_formatted(state: Dict, n: int = 5) -> str:
    """
    Get formatted string of recent history.
    
    Args:
        state: Current state dict
        n: Number of messages to include
        
    Returns:
        Formatted history string
    """
    messages = get_recent_history(state, n)
    
    if not messages:
        return "(No messages yet)"
    
    formatted_lines = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        name = msg.get("agent_name", "Unknown")
        content = msg.get("content", "")
        formatted_lines.append(f"[{role}] {name}: {content}")
    
    return "\n\n".join(formatted_lines)


def get_messages_by_agent(state: Dict, agent_id: str) -> List[Dict]:
    """
    Get all messages from a specific agent.
    
    Args:
        state: Current state dict
        agent_id: Agent ID to filter by
        
    Returns:
        List of message dicts from this agent
    """
    messages = state.get("messages", [])
    return [msg for msg in messages if msg.get("agent_id") == agent_id]


def get_messages_by_round(state: Dict, round_number: int) -> List[Dict]:
    """
    Get all messages from a specific round.
    
    Args:
        state: Current state dict
        round_number: Round to filter by
        
    Returns:
        List of message dicts from this round
    """
    messages = state.get("messages", [])
    return [msg for msg in messages if msg.get("round_number") == round_number]


def get_votes_by_round(state: Dict, round_number: int) -> List[Dict]:
    """
    Get all votes from a specific round.
    
    Args:
        state: Current state dict
        round_number: Round to filter by
        
    Returns:
        List of vote dicts from this round
    """
    # Collect votes from all rounds stored in switch history
    all_votes = []
    for switch in state.get("agent_switches", []):
        if switch.get("round_number") == round_number:
            # Votes that led to this switch are captured in vote_tally
            pass
    
    # Also check current votes if we're in the specified round
    if state.get("current_round") == round_number:
        all_votes.extend(state.get("current_votes", []))
    
    return all_votes


def get_switch_history(state: Dict) -> List[Dict]:
    """
    Get complete switch history.
    
    Args:
        state: Current state dict
        
    Returns:
        List of switch dicts
    """
    return state.get("agent_switches", [])


def get_current_debaters(state: Dict) -> Dict[str, str]:
    """
    Get current active debaters.
    
    Args:
        state: Current state dict
        
    Returns:
        Dict with 'proposition' and 'opposition' agent IDs
    """
    return {
        "proposition": state.get("active_proposition_id"),
        "opposition": state.get("opposition_id")
    }


def get_observers(state: Dict) -> List[str]:
    """
    Get list of observer agent IDs.
    
    Args:
        state: Current state dict
        
    Returns:
        List of observer agent IDs
    """
    return state.get("observer_ids", [])


def get_statistics(state: Dict) -> Dict[str, Any]:
    """
    Calculate debate statistics.
    
    Args:
        state: Current state dict
        
    Returns:
        Dict with various statistics
    """
    messages = state.get("messages", [])
    
    # Count messages per agent
    agent_message_counts = {}
    agent_word_counts = {}
    
    for msg in messages:
        agent_id = msg.get("agent_id", "unknown")
        agent_name = msg.get("agent_name", "Unknown")
        key = f"{agent_name} ({agent_id})"
        
        agent_message_counts[key] = agent_message_counts.get(key, 0) + 1
        
        word_count = len(msg.get("content", "").split())
        agent_word_counts[key] = agent_word_counts.get(key, 0) + word_count
    
    # Calculate averages
    total_words = sum(agent_word_counts.values())
    total_messages = len(messages)
    avg_message_length = total_words / total_messages if total_messages > 0 else 0
    
    # Switch statistics
    switches = state.get("agent_switches", [])
    
    return {
        "total_messages": total_messages,
        "total_words": total_words,
        "average_message_length": round(avg_message_length, 1),
        "messages_per_agent": agent_message_counts,
        "words_per_agent": agent_word_counts,
        "total_rounds": state.get("current_round", 1),
        "total_switches": len(switches),
        "elapsed_seconds": state.get("elapsed_seconds", 0),
        "duration": state.get("duration", 0),
        "phase": state.get("phase", "unknown"),
        "status": state.get("status", "unknown")
    }


def get_debate_summary(state: Dict) -> Dict[str, Any]:
    """
    Get a summary of the debate for the moderator.
    
    Args:
        state: Current state dict
        
    Returns:
        Summary dict suitable for moderation task
    """
    return {
        "topic": state.get("topic"),
        "duration_seconds": state.get("elapsed_seconds", 0),
        "total_rounds": state.get("current_round", 1),
        "total_messages": len(state.get("messages", [])),
        "total_switches": len(state.get("agent_switches", [])),
        "messages": state.get("messages", []),
        "switches": state.get("agent_switches", []),
        "final_proposition_agent": state.get("active_proposition_id"),
        "opposition_agent": state.get("opposition_id")
    }


def get_full_transcript(state: Dict) -> List[Dict]:
    """
    Get the full debate transcript formatted for moderation.
    
    Args:
        state: Current state dict
        
    Returns:
        List of dicts with 'speaker', 'role', 'content'
    """
    messages = state.get("messages", [])
    
    return [
        {
            "speaker": msg.get("agent_name", "Unknown"),
            "role": msg.get("role", "unknown"),
            "content": msg.get("content", "")
        }
        for msg in messages
    ]


def get_vote_history(state: Dict) -> List[Dict]:
    """
    Get vote history formatted for moderation.
    
    Args:
        state: Current state dict
        
    Returns:
        List of vote event dicts
    """
    # Reconstruct vote history from switches
    vote_events = []
    
    for switch in state.get("agent_switches", []):
        vote_events.append({
            "voter": "Multiple Observers",
            "voted_for": switch.get("old_agent_name", "Unknown"),
            "vote_type": "out",
            "reasoning": switch.get("reason", "")
        })
    
    return vote_events

