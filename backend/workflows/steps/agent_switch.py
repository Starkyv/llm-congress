"""
Agent Switch Step

Handles switching proposition agents when voted out.
"""

import sys
import os
from typing import Dict, Any, Generator
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state import record_agent_switch, get_available_replacement
from workflows.config import DebateEvent, DebateEventType
from workflows.steps.initialize import get_agent_by_id


def handle_agent_switch(
    state: Dict[str, Any],
    decision: str
) -> Generator[DebateEvent, None, Dict[str, Any]]:
    """
    Handle agent switch decision.
    
    Args:
        state: Current debate state
        decision: "switch" or "stay"
        
    Yields:
        DebateEvent objects for streaming
        
    Returns:
        Updated state dict
    """
    if decision != "switch":
        # No switch needed, emit stay event
        active_id = state.get("active_proposition_id")
        active_agent = get_agent_by_id(active_id)
        active_name = active_agent.name if active_agent else "Unknown"
        
        yield DebateEvent(
            event_type=DebateEventType.PHASE_CHANGE,
            data={
                "message": f"{active_name} stays in the debate",
                "action": "stay",
                "agent_id": active_id,
                "agent_name": active_name,
            },
            timestamp=datetime.now().isoformat()
        )
        
        return state
    
    # Get old agent info
    old_id = state.get("active_proposition_id")
    old_agent = get_agent_by_id(old_id)
    old_name = old_agent.name if old_agent else "Unknown"
    
    # Find replacement
    new_id = get_available_replacement(state)
    
    if not new_id:
        # No replacements available
        yield DebateEvent(
            event_type=DebateEventType.WARNING,
            data={
                "message": "No replacement agents available. Continuing with current agent.",
                "agent_id": old_id,
            },
            timestamp=datetime.now().isoformat()
        )
        return state
    
    # Get new agent info
    new_agent = get_agent_by_id(new_id)
    new_name = new_agent.name if new_agent else "Unknown"
    
    # Record switch
    vote_tally = state.get("vote_tally", {"in": 0, "out": 0})
    reason = f"Voted out with {vote_tally.get('out', 0)} out votes vs {vote_tally.get('in', 0)} in votes"
    
    state = record_agent_switch(
        state,
        old_agent_id=old_id,
        old_agent_name=old_name,
        new_agent_id=new_id,
        new_agent_name=new_name,
        reason=reason
    )
    
    # Emit switch event
    yield DebateEvent(
        event_type=DebateEventType.AGENT_SWITCH,
        data={
            "old_agent_id": old_id,
            "old_agent_name": old_name,
            "new_agent_id": new_id,
            "new_agent_name": new_name,
            "reason": reason,
            "vote_tally": vote_tally,
            "round_number": state.get("current_round", 1),
        },
        timestamp=datetime.now().isoformat()
    )
    
    return state

