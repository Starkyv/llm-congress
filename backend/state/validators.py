"""
Debate State Validators

Custom validation logic for debate state.
"""

from typing import Dict, List, Optional
from datetime import datetime


def validate_state_structure(state: Dict) -> tuple[bool, List[str]]:
    """
    Validate that state has all required fields.
    
    Args:
        state: The state dict to validate
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Required configuration fields
    required_config = ["topic", "duration", "exchanges_per_round"]
    for field in required_config:
        if field not in state:
            errors.append(f"Missing required config field: {field}")
    
    # Required agent fields
    required_agent = ["active_proposition_id", "opposition_id", "all_proposition_ids"]
    for field in required_agent:
        if field not in state:
            errors.append(f"Missing required agent field: {field}")
    
    # Required state fields
    required_state = ["messages", "current_round", "phase", "status"]
    for field in required_state:
        if field not in state:
            errors.append(f"Missing required state field: {field}")
    
    return len(errors) == 0, errors


def validate_phase_transition(
    current_phase: str,
    new_phase: str
) -> tuple[bool, Optional[str]]:
    """
    Validate if a phase transition is allowed.
    
    Args:
        current_phase: Current phase
        new_phase: Proposed new phase
        
    Returns:
        Tuple of (is_valid, error message if invalid)
    """
    valid_transitions = {
        "initializing": ["debating"],
        "debating": ["voting", "concluding", "completed"],
        "voting": ["debating", "concluding"],
        "concluding": ["completed"],
        "completed": []
    }
    
    allowed = valid_transitions.get(current_phase, [])
    
    if new_phase in allowed:
        return True, None
    else:
        return False, f"Invalid transition from '{current_phase}' to '{new_phase}'. Allowed: {allowed}"


def validate_vote(vote: str) -> tuple[bool, Optional[str]]:
    """
    Validate a vote value.
    
    Args:
        vote: The vote value to validate
        
    Returns:
        Tuple of (is_valid, error message if invalid)
    """
    if vote.lower() not in ["in", "out"]:
        return False, f"Invalid vote '{vote}'. Must be 'in' or 'out'."
    return True, None


def validate_role(role: str) -> tuple[bool, Optional[str]]:
    """
    Validate a debate role.
    
    Args:
        role: The role to validate
        
    Returns:
        Tuple of (is_valid, error message if invalid)
    """
    if role.lower() not in ["proposition", "opposition"]:
        return False, f"Invalid role '{role}'. Must be 'proposition' or 'opposition'."
    return True, None


def validate_agent_in_debate(state: Dict, agent_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate that an agent is part of the debate.
    
    Args:
        state: Current state
        agent_id: Agent ID to check
        
    Returns:
        Tuple of (is_valid, error message if invalid)
    """
    all_agents = (
        state.get("all_proposition_ids", []) + 
        [state.get("opposition_id")]
    )
    
    if agent_id not in all_agents:
        return False, f"Agent '{agent_id}' is not part of this debate."
    return True, None


def validate_can_vote(state: Dict, voter_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate that an agent can vote (must be an observer).
    
    Args:
        state: Current state
        voter_id: Voter ID to check
        
    Returns:
        Tuple of (is_valid, error message if invalid)
    """
    if state.get("phase") != "voting":
        return False, "Cannot vote outside of voting phase."
    
    observer_ids = state.get("observer_ids", [])
    if voter_id not in observer_ids:
        return False, f"Agent '{voter_id}' is not an observer and cannot vote."
    
    # Check if already voted
    current_votes = state.get("current_votes", [])
    for vote in current_votes:
        if vote.get("voter_id") == voter_id:
            return False, f"Agent '{voter_id}' has already voted in this round."
    
    return True, None


def validate_exchanges_complete(state: Dict) -> bool:
    """
    Check if enough exchanges have occurred for a voting round.
    
    Args:
        state: Current state
        
    Returns:
        True if exchanges_per_round reached
    """
    current_exchange = state.get("current_exchange", 0)
    exchanges_per_round = state.get("exchanges_per_round", 3)
    
    return current_exchange >= exchanges_per_round


def validate_time_remaining(state: Dict) -> bool:
    """
    Check if debate still has time remaining.
    
    Args:
        state: Current state
        
    Returns:
        True if time remaining
    """
    elapsed = state.get("elapsed_seconds", 0)
    duration = state.get("duration", 300)
    
    return elapsed < duration

