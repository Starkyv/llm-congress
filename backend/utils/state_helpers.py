"""
State Helper Functions

Common helper functions for working with debate state.
"""

from typing import Dict, List, Optional
from datetime import datetime


def format_message_for_context(message: Dict) -> str:
    """
    Format a single message for context display.
    
    Args:
        message: Message dict from state
        
    Returns:
        Formatted string
    """
    role = message.get("role", "unknown").upper()
    name = message.get("agent_name", "Unknown")
    content = message.get("content", "")
    
    return f"[{role}] {name}: {content}"


def format_messages_for_context(messages: List[Dict], max_messages: int = 5) -> str:
    """
    Format multiple messages for context display.
    
    Args:
        messages: List of message dicts
        max_messages: Maximum messages to include
        
    Returns:
        Formatted string with all messages
    """
    recent = messages[-max_messages:] if len(messages) > max_messages else messages
    
    formatted = [format_message_for_context(msg) for msg in recent]
    return "\n\n".join(formatted)


def format_vote_for_display(vote: Dict) -> str:
    """
    Format a vote for display.
    
    Args:
        vote: Vote dict from state
        
    Returns:
        Formatted string
    """
    voter = vote.get("voter_name", "Unknown")
    decision = vote.get("vote", "unknown")
    reasoning = vote.get("reasoning", "")
    
    return f"{voter} voted '{decision}': {reasoning}"


def format_vote_tally(tally: Dict[str, int]) -> str:
    """
    Format vote tally for display.
    
    Args:
        tally: Dict with 'in' and 'out' counts
        
    Returns:
        Formatted string
    """
    in_votes = tally.get("in", 0)
    out_votes = tally.get("out", 0)
    
    return f"IN: {in_votes} | OUT: {out_votes}"


def format_switch_for_display(switch: Dict) -> str:
    """
    Format an agent switch for display.
    
    Args:
        switch: AgentSwitch dict from state
        
    Returns:
        Formatted string
    """
    old_name = switch.get("old_agent_name", "Unknown")
    new_name = switch.get("new_agent_name", "Unknown")
    reason = switch.get("reason", "")
    round_num = switch.get("round_number", 0)
    
    return f"Round {round_num}: {old_name} → {new_name} ({reason})"


def format_time_elapsed(seconds: int) -> str:
    """
    Format elapsed time for display.
    
    Args:
        seconds: Elapsed seconds
        
    Returns:
        Formatted time string (MM:SS)
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def format_time_remaining(elapsed: int, duration: int) -> str:
    """
    Format remaining time for display.
    
    Args:
        elapsed: Elapsed seconds
        duration: Total duration seconds
        
    Returns:
        Formatted time string (MM:SS)
    """
    remaining = max(0, duration - elapsed)
    return format_time_elapsed(remaining)


def get_agent_message_count(messages: List[Dict], agent_id: str) -> int:
    """
    Count messages from a specific agent.
    
    Args:
        messages: List of message dicts
        agent_id: Agent ID to count
        
    Returns:
        Number of messages from this agent
    """
    return sum(1 for msg in messages if msg.get("agent_id") == agent_id)


def get_agent_word_count(messages: List[Dict], agent_id: str) -> int:
    """
    Total word count from a specific agent.
    
    Args:
        messages: List of message dicts
        agent_id: Agent ID to count
        
    Returns:
        Total words from this agent
    """
    total = 0
    for msg in messages:
        if msg.get("agent_id") == agent_id:
            content = msg.get("content", "")
            total += len(content.split())
    return total


def get_last_speaker(messages: List[Dict]) -> Optional[str]:
    """
    Get ID of the last speaker.
    
    Args:
        messages: List of message dicts
        
    Returns:
        Agent ID of last speaker, or None
    """
    if not messages:
        return None
    return messages[-1].get("agent_id")


def get_last_message_content(messages: List[Dict]) -> Optional[str]:
    """
    Get content of the last message.
    
    Args:
        messages: List of message dicts
        
    Returns:
        Content of last message, or None
    """
    if not messages:
        return None
    return messages[-1].get("content")


def should_trigger_voting(state: Dict) -> bool:
    """
    Check if voting should be triggered based on exchange count.
    
    Args:
        state: Current state dict
        
    Returns:
        True if voting should start
    """
    current_exchange = state.get("current_exchange", 0)
    exchanges_per_round = state.get("exchanges_per_round", 3)
    phase = state.get("phase", "initializing")
    
    return (
        phase == "debating" and
        current_exchange >= exchanges_per_round
    )


def should_end_debate(state: Dict) -> bool:
    """
    Check if debate should end.
    
    Args:
        state: Current state dict
        
    Returns:
        True if debate should end
    """
    elapsed = state.get("elapsed_seconds", 0)
    duration = state.get("duration", 300)
    phase = state.get("phase", "initializing")
    
    return elapsed >= duration and phase != "completed"


def get_next_speaker_role(messages: List[Dict]) -> str:
    """
    Determine which role should speak next.
    
    Args:
        messages: List of message dicts
        
    Returns:
        "proposition" or "opposition"
    """
    if not messages:
        return "proposition"  # Proposition starts
    
    last_role = messages[-1].get("role", "proposition")
    return "opposition" if last_role == "proposition" else "proposition"

