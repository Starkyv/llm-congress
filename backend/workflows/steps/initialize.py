"""
Initialize Step

Sets up the debate environment: loads agents, creates initial state.
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state import initialize_state, set_phase
from agents import (
    get_all_proposition_agents,
    get_opposition_agent,
    get_moderator_agent,
    select_random_proposition,
    get_agent_info,
)
from workflows.config import DebateEvent, DebateEventType


def initialize_debate(
    topic: str,
    duration: int = 300,
    exchanges_per_round: int = 3,
    first_agent_id: Optional[str] = None
) -> tuple[Dict[str, Any], DebateEvent]:
    """
    Initialize the debate environment.
    
    Args:
        topic: The debate topic
        duration: Duration in seconds
        exchanges_per_round: Exchanges before voting
        first_agent_id: Optional specific first agent
        
    Returns:
        Tuple of (initial state dict, start event)
    """
    # Load all agents
    proposition_agents = get_all_proposition_agents()
    opposition_agent = get_opposition_agent()
    moderator_agent = get_moderator_agent()
    
    # Validate agents loaded
    if not proposition_agents:
        raise ValueError("No proposition agents could be loaded")
    if not opposition_agent:
        raise ValueError("Opposition agent could not be loaded")
    
    # Get agent IDs
    all_proposition_ids = [agent.agent_id for agent in proposition_agents]
    opposition_id = opposition_agent.agent_id
    
    # Select first debater
    if first_agent_id and first_agent_id in all_proposition_ids:
        active_proposition_id = first_agent_id
    else:
        # Random selection
        first_agent = select_random_proposition()
        active_proposition_id = first_agent.agent_id
    
    # Get observer IDs (all proposition agents except active one)
    observer_ids = [aid for aid in all_proposition_ids if aid != active_proposition_id]
    
    # Create initial state
    state = initialize_state(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges_per_round,
        all_proposition_ids=all_proposition_ids,
        opposition_id=opposition_id,
        active_proposition_id=active_proposition_id,
        observer_ids=observer_ids
    )
    
    # Set phase to debating
    state = set_phase(state, "debating")
    
    # Get agent names for event
    active_agent = next(
        (a for a in proposition_agents if a.agent_id == active_proposition_id),
        None
    )
    active_agent_name = active_agent.name if active_agent else "Unknown"
    
    # Create start event
    start_event = DebateEvent(
        event_type=DebateEventType.DEBATE_STARTED,
        data={
            "topic": topic,
            "duration": duration,
            "exchanges_per_round": exchanges_per_round,
            "first_debater": active_agent_name,
            "first_debater_id": active_proposition_id,
            "opposition": opposition_agent.name,
            "observers": [
                a.name for a in proposition_agents 
                if a.agent_id in observer_ids
            ],
            "total_agents": len(proposition_agents) + 2,  # +2 for opposition and moderator
        },
        timestamp=datetime.now().isoformat()
    )
    
    return state, start_event


def get_agent_by_id(agent_id: str):
    """Get agent object by ID"""
    proposition_agents = get_all_proposition_agents()
    opposition_agent = get_opposition_agent()
    moderator_agent = get_moderator_agent()
    
    for agent in proposition_agents:
        if agent.agent_id == agent_id:
            return agent
    
    if opposition_agent.agent_id == agent_id:
        return opposition_agent
    
    if moderator_agent.agent_id == agent_id:
        return moderator_agent
    
    return None

