"""
Streaming Module

Provides Server-Sent Events (SSE) streaming for the debate workflow.
Uses Agno's CustomEvent pattern for event definitions.

Based on Agno's custom events documentation:
https://docs.agno.com/basics/agents/running-agents#custom-events

Usage:
    from streaming import SSEHandler, DebateStartedEvent, event_to_sse
    
    # Create custom events
    event = DebateStartedEvent(topic="UBI", duration=300)
    
    # Convert to SSE format
    sse_message = event_to_sse(event)
    
    # Or use SSE handler
    handler = SSEHandler()
    for sse in handler.stream_events(event_generator):
        yield sse
"""

from .events import (
    # Event types enum
    DebateEventType,
    
    # Custom events (extend Agno's CustomEvent)
    DebateStartedEvent,
    AgentMessageChunkEvent,
    AgentMessageCompleteEvent,
    VotingInitiatedEvent,
    VoteCastEvent,
    VotingCompleteEvent,
    AgentSwitchEvent,
    TimerUpdateEvent,
    PhaseChangeEvent,
    ModeratorMessageChunkEvent,
    ModeratorMessageCompleteEvent,
    DebateCompleteEvent,
    DebateErrorEvent,
    DebateWarningEvent,
    
    # Helpers
    event_to_sse,
    create_event_from_dict,
)

from .sse_handler import (
    SSEHandler,
    EventBuffer,
)

__all__ = [
    # Event types
    'DebateEventType',
    
    # Custom Agno events
    'DebateStartedEvent',
    'AgentMessageChunkEvent',
    'AgentMessageCompleteEvent',
    'VotingInitiatedEvent',
    'VoteCastEvent',
    'VotingCompleteEvent',
    'AgentSwitchEvent',
    'TimerUpdateEvent',
    'PhaseChangeEvent',
    'ModeratorMessageChunkEvent',
    'ModeratorMessageCompleteEvent',
    'DebateCompleteEvent',
    'DebateErrorEvent',
    'DebateWarningEvent',
    
    # Helpers
    'event_to_sse',
    'create_event_from_dict',
    
    # Handlers
    'SSEHandler',
    'EventBuffer',
]

