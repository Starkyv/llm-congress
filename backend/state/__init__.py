"""
Debate State Module

Provides state management for debates using Agno Workflow session_state.

This module follows Agno's Workflow State pattern where:
- State is initialized when workflow starts
- State flows through all workflow steps automatically
- State can be accessed via run_context.session_state in tools
- State changes persist across workflow steps

Usage with Agno Workflow:
    from agno.workflow import Workflow
    from state import DebateState, initialize_state
    
    # Initialize state
    initial_state = initialize_state(
        topic="My Debate Topic",
        duration=300,
        ...
    )
    
    # Create workflow with state
    workflow = Workflow(
        name="Debate",
        session_state=initial_state,
        steps=[...]
    )

Usage in Workflow Tools:
    from agno.run import RunContext
    from state import add_message
    
    def debate_tool(run_context: RunContext, content: str):
        # Access and modify state
        state = run_context.session_state
        add_message(state, agent_id="...", content=content, ...)
"""

# Models
from .models import (
    Message,
    Vote,
    AgentSwitch,
    DebateState,
    DebateStateDict,
)

# Operations
from .operations import (
    initialize_state,
    add_message,
    start_voting_round,
    add_vote,
    complete_voting_round,
    record_agent_switch,
    update_timer,
    set_phase,
    set_error,
    get_available_replacement,
)

# Validators
from .validators import (
    validate_state_structure,
    validate_phase_transition,
    validate_vote,
    validate_role,
    validate_agent_in_debate,
    validate_can_vote,
    validate_exchanges_complete,
    validate_time_remaining,
)

__all__ = [
    # Models
    'Message',
    'Vote',
    'AgentSwitch',
    'DebateState',
    'DebateStateDict',
    # Operations
    'initialize_state',
    'add_message',
    'start_voting_round',
    'add_vote',
    'complete_voting_round',
    'record_agent_switch',
    'update_timer',
    'set_phase',
    'set_error',
    'get_available_replacement',
    # Validators
    'validate_state_structure',
    'validate_phase_transition',
    'validate_vote',
    'validate_role',
    'validate_agent_in_debate',
    'validate_can_vote',
    'validate_exchanges_complete',
    'validate_time_remaining',
]

