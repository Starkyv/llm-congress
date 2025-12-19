"""
Debate Workflow Configuration

Configuration settings and event types for the debate workflow.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DebateEventType(str, Enum):
    """Event types emitted during debate workflow"""
    # Lifecycle events
    DEBATE_STARTED = "debate_started"
    DEBATE_COMPLETE = "debate_complete"
    PHASE_CHANGE = "phase_change"
    
    # Message events
    AGENT_MESSAGE_CHUNK = "agent_message_chunk"
    AGENT_MESSAGE_COMPLETE = "agent_message_complete"
    
    # Voting events
    VOTING_INITIATED = "voting_initiated"
    VOTE_CAST = "vote_cast"
    VOTING_COMPLETE = "voting_complete"
    
    # Agent events
    AGENT_SWITCH = "agent_switch"
    
    # Timer events
    TIMER_UPDATE = "timer_update"
    
    # Moderator events
    MODERATOR_MESSAGE_CHUNK = "moderator_message_chunk"
    MODERATOR_MESSAGE_COMPLETE = "moderator_message_complete"
    
    # Error events
    ERROR = "error"
    WARNING = "warning"


class DebateEvent(BaseModel):
    """A debate workflow event for streaming to clients"""
    event_type: DebateEventType
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None
    
    def to_sse_format(self) -> str:
        """Format event for Server-Sent Events"""
        import json
        return f"event: {self.event_type.value}\ndata: {json.dumps(self.data)}\n\n"


class DebateWorkflowConfig(BaseModel):
    """Configuration for a debate workflow run"""
    topic: str = Field(..., description="The debate topic/proposition")
    duration: int = Field(default=300, description="Debate duration in seconds")
    exchanges_per_round: int = Field(default=3, description="Exchanges before voting")
    first_agent_id: Optional[str] = Field(default=None, description="First proposition agent ID")
    enable_streaming: bool = Field(default=True, description="Enable streaming events")
    stream_chunk_delay: float = Field(default=0.05, description="Delay between stream chunks")
    
    class Config:
        extra = "allow"


# Workflow metadata
WORKFLOW_NAME = "Debate Simulation"
WORKFLOW_VERSION = "1.0.0"
WORKFLOW_DESCRIPTION = "Multi-agent debate with voting and moderation"
WORKFLOW_TAGS = ["debate", "multi-agent", "simulation"]

