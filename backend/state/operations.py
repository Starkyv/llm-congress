"""
Debate State Operations

Functions to safely modify debate state within Agno workflows.
These operations are designed to work with run_context.session_state.

Usage in Agno workflow tools:
    def my_tool(run_context: RunContext, ...):
        # Access state
        state = run_context.session_state
        
        # Modify state using operations
        add_message(state, agent_id="...", ...)
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Literal
from .models import Message, Vote, AgentSwitch, DebateState


def initialize_state(
    topic: str,
    duration: int,
    exchanges_per_round: int,
    all_proposition_ids: List[str],
    opposition_id: str,
    active_proposition_id: str,
    observer_ids: Optional[List[str]] = None
) -> Dict:
    """
    Initialize debate state when debate starts.
    
    Args:
        topic: The debate topic
        duration: Total duration in seconds
        exchanges_per_round: Number of exchanges before voting
        all_proposition_ids: All available proposition agent IDs
        opposition_id: Opposition agent ID
        active_proposition_id: First active proposition agent ID
        observer_ids: IDs of observing agents (proposition agents not active)
        
    Returns:
        Initial state as dict for workflow session_state
    """
    if observer_ids is None:
        observer_ids = [aid for aid in all_proposition_ids if aid != active_proposition_id]
    
    state = DebateState(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges_per_round,
        active_proposition_id=active_proposition_id,
        opposition_id=opposition_id,
        observer_ids=observer_ids,
        all_proposition_ids=all_proposition_ids,
        messages=[],
        current_round=1,
        current_exchange=0,
        current_votes=[],
        vote_tally={"in": 0, "out": 0},
        evaluating_agent_id=None,
        agent_switches=[],
        start_time=datetime.now(),
        elapsed_seconds=0,
        paused_seconds=0,
        is_paused=False,
        phase="initializing",
        status="running",
        error_message=None
    )
    
    return state.model_dump_for_workflow()


def add_message(
    state: Dict,
    agent_id: str,
    agent_name: str,
    role: Literal["proposition", "opposition"],
    content: str,
    timestamp: datetime = None
) -> Dict:
    """
    Record a new debate message.
    
    Args:
        state: Current session state dict
        agent_id: ID of speaking agent
        agent_name: Name of speaking agent
        role: "proposition" or "opposition"
        content: The argument content
        timestamp: When message was created (default: now)
        
    Returns:
        Updated state dict
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    message = Message(
        agent_id=agent_id,
        agent_name=agent_name,
        role=role,
        content=content,
        timestamp=timestamp,
        round_number=state["current_round"]
    )
    
    # Append message
    state["messages"].append(message.model_dump(mode='json'))
    
    # Increment exchange counter
    state["current_exchange"] = state.get("current_exchange", 0) + 1
    
    return state


def start_voting_round(
    state: Dict,
    evaluating_agent_id: str
) -> Dict:
    """
    Prepare state for voting phase.
    
    Args:
        state: Current session state dict
        evaluating_agent_id: ID of agent being evaluated
        
    Returns:
        Updated state dict
    """
    state["phase"] = "voting"
    state["evaluating_agent_id"] = evaluating_agent_id
    state["current_votes"] = []
    state["vote_tally"] = {"in": 0, "out": 0}
    state["is_paused"] = True  # Pause timer during voting
    
    return state


def add_vote(
    state: Dict,
    voter_id: str,
    voter_name: str,
    vote: Literal["in", "out"],
    reasoning: str,
    timestamp: datetime = None
) -> Dict:
    """
    Record a single vote.
    
    Args:
        state: Current session state dict
        voter_id: ID of voting agent
        voter_name: Name of voting agent
        vote: "in" or "out"
        reasoning: Explanation for vote
        timestamp: When vote was cast (default: now)
        
    Returns:
        Updated state dict
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    vote_obj = Vote(
        voter_id=voter_id,
        voter_name=voter_name,
        evaluating_agent_id=state["evaluating_agent_id"],
        vote=vote,
        reasoning=reasoning,
        timestamp=timestamp,
        round_number=state["current_round"]
    )
    
    # Append vote
    state["current_votes"].append(vote_obj.model_dump(mode='json'))
    
    # Update tally
    state["vote_tally"][vote] = state["vote_tally"].get(vote, 0) + 1
    
    return state


def complete_voting_round(state: Dict) -> Tuple[Dict, Literal["switch", "stay"]]:
    """
    Finalize voting and decide outcome.
    
    Args:
        state: Current session state dict
        
    Returns:
        Tuple of (updated state dict, decision: "switch" or "stay")
    """
    in_votes = state["vote_tally"].get("in", 0)
    out_votes = state["vote_tally"].get("out", 0)
    
    # Determine outcome
    decision: Literal["switch", "stay"] = "switch" if out_votes > in_votes else "stay"
    
    # Resume timer
    state["is_paused"] = False
    
    # Reset for next round
    state["phase"] = "debating"
    state["current_exchange"] = 0
    state["current_round"] = state.get("current_round", 1) + 1
    
    return state, decision


def record_agent_switch(
    state: Dict,
    old_agent_id: str,
    old_agent_name: str,
    new_agent_id: str,
    new_agent_name: str,
    reason: str
) -> Dict:
    """
    Log an agent switch.
    
    Args:
        state: Current session state dict
        old_agent_id: ID of replaced agent
        old_agent_name: Name of replaced agent
        new_agent_id: ID of new agent
        new_agent_name: Name of new agent
        reason: Why switch occurred
        
    Returns:
        Updated state dict
    """
    switch = AgentSwitch(
        old_agent_id=old_agent_id,
        old_agent_name=old_agent_name,
        new_agent_id=new_agent_id,
        new_agent_name=new_agent_name,
        reason=reason,
        vote_tally=dict(state["vote_tally"]),
        round_number=state["current_round"],
        timestamp=datetime.now()
    )
    
    # Append switch
    state["agent_switches"].append(switch.model_dump(mode='json'))
    
    # Update active agent
    state["active_proposition_id"] = new_agent_id
    
    # Update observers (old becomes observer, new becomes active)
    observer_ids = state.get("observer_ids", [])
    if old_agent_id not in observer_ids:
        observer_ids.append(old_agent_id)
    if new_agent_id in observer_ids:
        observer_ids.remove(new_agent_id)
    state["observer_ids"] = observer_ids
    
    return state


def update_timer(state: Dict) -> Dict:
    """
    Update elapsed time in state.
    
    Args:
        state: Current session state dict
        
    Returns:
        Updated state dict
    """
    if not state.get("is_paused", False):
        start_time = state.get("start_time")
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        
        total_elapsed = (datetime.now() - start_time).total_seconds()
        paused = state.get("paused_seconds", 0)
        state["elapsed_seconds"] = int(total_elapsed - paused)
    
    return state


def set_phase(
    state: Dict,
    new_phase: Literal["initializing", "debating", "voting", "concluding", "completed"]
) -> Dict:
    """
    Transition to a new debate phase.
    
    Args:
        state: Current session state dict
        new_phase: The new phase to set
        
    Returns:
        Updated state dict
    """
    # Valid transitions
    valid_transitions = {
        "initializing": ["debating"],
        "debating": ["voting", "concluding", "completed"],
        "voting": ["debating", "concluding"],
        "concluding": ["completed"],
        "completed": []
    }
    
    current_phase = state.get("phase", "initializing")
    
    if new_phase in valid_transitions.get(current_phase, []):
        state["phase"] = new_phase
        
        # Special handling for completed phase
        if new_phase == "completed":
            state["status"] = "completed"
    else:
        # Log warning but allow transition for flexibility
        state["phase"] = new_phase
    
    return state


def set_error(state: Dict, error_message: str) -> Dict:
    """
    Set error state.
    
    Args:
        state: Current session state dict
        error_message: Description of the error
        
    Returns:
        Updated state dict
    """
    state["status"] = "error"
    state["error_message"] = error_message
    
    return state


def get_available_replacement(state: Dict) -> Optional[str]:
    """
    Get an available agent to replace the current active proposition agent.
    
    Args:
        state: Current session state dict
        
    Returns:
        Agent ID of available replacement, or None if no replacements
    """
    observer_ids = state.get("observer_ids", [])
    
    if observer_ids:
        return observer_ids[0]  # Return first available observer
    
    return None

