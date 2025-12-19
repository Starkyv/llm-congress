"""
Debate Workflows Module

Provides the main debate workflow and supporting components.

Based on Agno Workflow patterns:
https://docs.agno.com/basics/workflows/overview

Usage:
    from workflows import DebateWorkflow, create_debate_workflow
    
    # Create workflow
    workflow = create_debate_workflow()
    
    # Run with streaming events
    for event in workflow.run(topic="UBI should be implemented", duration=300):
        print(f"{event.event_type}: {event.data}")
    
    # Or run synchronously
    final_state = workflow.run_sync(topic="UBI", duration=60)
"""

from .config import (
    DebateWorkflowConfig,
    DebateEvent,
    DebateEventType,
    WORKFLOW_NAME,
    WORKFLOW_VERSION,
    WORKFLOW_DESCRIPTION,
    WORKFLOW_TAGS,
)

from .debate_workflow import (
    DebateWorkflow,
    create_debate_workflow,
    create_agno_workflow,
)

from .steps import (
    initialize_debate,
    proposition_turn,
    opposition_turn,
    conduct_voting,
    handle_agent_switch,
    conclude_debate,
)

__all__ = [
    # Main workflow
    'DebateWorkflow',
    'create_debate_workflow',
    'create_agno_workflow',
    # Config
    'DebateWorkflowConfig',
    'DebateEvent',
    'DebateEventType',
    'WORKFLOW_NAME',
    'WORKFLOW_VERSION',
    'WORKFLOW_DESCRIPTION',
    'WORKFLOW_TAGS',
    # Steps
    'initialize_debate',
    'proposition_turn',
    'opposition_turn',
    'conduct_voting',
    'handle_agent_switch',
    'conclude_debate',
]

