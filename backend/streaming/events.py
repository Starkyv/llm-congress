"""
Agno Custom Events for Debate Workflow

Based on Agno's CustomEvent pattern:
https://docs.agno.com/basics/agents/running-agents#custom-events

These custom events can be yielded from tools and will be handled
alongside Agno's built-in events when streaming.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# Import Agno's CustomEvent base class
try:
    from agno.run.agent import CustomEvent
except ImportError:
    # Fallback if CustomEvent not available
    @dataclass
    class CustomEvent:
        """Fallback CustomEvent base class"""
        pass


class DebateEventType(str, Enum):
    """Event types for debate workflow"""
    # Lifecycle
    DEBATE_STARTED = "debate_started"
    DEBATE_COMPLETE = "debate_complete"
    PHASE_CHANGE = "phase_change"
    
    # Messages
    AGENT_MESSAGE_CHUNK = "agent_message_chunk"
    AGENT_MESSAGE_COMPLETE = "agent_message_complete"
    
    # Voting
    VOTING_INITIATED = "voting_initiated"
    VOTE_CAST = "vote_cast"
    VOTING_COMPLETE = "voting_complete"
    
    # Agent management
    AGENT_SWITCH = "agent_switch"
    
    # Timer
    TIMER_UPDATE = "timer_update"
    
    # Moderator
    MODERATOR_MESSAGE_CHUNK = "moderator_message_chunk"
    MODERATOR_MESSAGE_COMPLETE = "moderator_message_complete"
    
    # Errors
    ERROR = "error"
    WARNING = "warning"


# === Custom Agno Events ===

@dataclass
class DebateStartedEvent(CustomEvent):
    """Event emitted when debate begins"""
    topic: str = ""
    duration: int = 0
    exchanges_per_round: int = 0
    first_debater_id: Optional[str] = None
    first_debater_name: Optional[str] = None
    opposition_name: Optional[str] = None
    observer_names: List[str] = field(default_factory=list)
    total_agents: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.DEBATE_STARTED.value


@dataclass
class AgentMessageChunkEvent(CustomEvent):
    """Event emitted for each chunk during streaming"""
    agent_id: str = ""
    agent_name: str = ""
    role: str = ""  # "proposition" or "opposition"
    chunk: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.AGENT_MESSAGE_CHUNK.value


@dataclass
class AgentMessageCompleteEvent(CustomEvent):
    """Event emitted when agent finishes speaking"""
    agent_id: str = ""
    agent_name: str = ""
    role: str = ""
    content: str = ""
    word_count: int = 0
    round_number: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.AGENT_MESSAGE_COMPLETE.value


@dataclass
class VotingInitiatedEvent(CustomEvent):
    """Event emitted when voting round begins"""
    evaluating_agent_id: str = ""
    evaluating_agent_name: str = ""
    round_number: int = 0
    observer_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.VOTING_INITIATED.value


@dataclass
class VoteCastEvent(CustomEvent):
    """Event emitted when an observer casts a vote"""
    voter_id: str = ""
    voter_name: str = ""
    vote: str = ""  # "in" or "out"
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.VOTE_CAST.value


@dataclass
class VotingCompleteEvent(CustomEvent):
    """Event emitted when all votes are tallied"""
    evaluating_agent_id: str = ""
    evaluating_agent_name: str = ""
    in_votes: int = 0
    out_votes: int = 0
    decision: str = ""  # "switch" or "stay"
    votes: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.VOTING_COMPLETE.value


@dataclass
class AgentSwitchEvent(CustomEvent):
    """Event emitted when proposition agent is switched"""
    old_agent_id: str = ""
    old_agent_name: str = ""
    new_agent_id: str = ""
    new_agent_name: str = ""
    reason: str = ""
    in_votes: int = 0
    out_votes: int = 0
    round_number: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.AGENT_SWITCH.value


@dataclass
class TimerUpdateEvent(CustomEvent):
    """Event emitted for timer updates"""
    elapsed_seconds: int = 0
    remaining_seconds: int = 0
    elapsed_formatted: str = ""
    remaining_formatted: str = ""
    is_paused: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.TIMER_UPDATE.value


@dataclass
class PhaseChangeEvent(CustomEvent):
    """Event emitted when debate phase changes"""
    old_phase: str = ""
    new_phase: str = ""
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.PHASE_CHANGE.value


@dataclass
class ModeratorMessageChunkEvent(CustomEvent):
    """Event emitted for moderator message chunks"""
    chunk: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.MODERATOR_MESSAGE_CHUNK.value


@dataclass 
class ModeratorMessageCompleteEvent(CustomEvent):
    """Event emitted when moderator finishes summary"""
    summary: str = ""
    word_count: int = 0
    is_fallback: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.MODERATOR_MESSAGE_COMPLETE.value


@dataclass
class DebateCompleteEvent(CustomEvent):
    """Event emitted when debate ends"""
    topic: str = ""
    duration_seconds: int = 0
    total_messages: int = 0
    total_rounds: int = 0
    total_switches: int = 0
    final_proposition_agent: str = ""
    summary_preview: str = ""
    statistics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.DEBATE_COMPLETE.value


@dataclass
class DebateErrorEvent(CustomEvent):
    """Event emitted on errors"""
    step: str = ""
    error: str = ""
    is_critical: bool = False
    agent_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.ERROR.value


@dataclass
class DebateWarningEvent(CustomEvent):
    """Event emitted for warnings"""
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def event_type(self) -> str:
        return DebateEventType.WARNING.value


# Helper function to convert event to SSE format
def event_to_sse(event: CustomEvent) -> str:
    """Convert a custom event to Server-Sent Events format"""
    import json
    from dataclasses import asdict
    
    event_type = getattr(event, 'event_type', 'unknown')
    data = asdict(event)
    
    # Remove the event_type from data since it's in the event line
    data.pop('event_type', None)
    
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


# Helper to create events from dict data (for backwards compatibility)
def create_event_from_dict(event_type: str, data: Dict[str, Any]) -> CustomEvent:
    """Create appropriate event from type and data dict"""
    event_map = {
        DebateEventType.DEBATE_STARTED.value: DebateStartedEvent,
        DebateEventType.AGENT_MESSAGE_CHUNK.value: AgentMessageChunkEvent,
        DebateEventType.AGENT_MESSAGE_COMPLETE.value: AgentMessageCompleteEvent,
        DebateEventType.VOTING_INITIATED.value: VotingInitiatedEvent,
        DebateEventType.VOTE_CAST.value: VoteCastEvent,
        DebateEventType.VOTING_COMPLETE.value: VotingCompleteEvent,
        DebateEventType.AGENT_SWITCH.value: AgentSwitchEvent,
        DebateEventType.TIMER_UPDATE.value: TimerUpdateEvent,
        DebateEventType.PHASE_CHANGE.value: PhaseChangeEvent,
        DebateEventType.MODERATOR_MESSAGE_CHUNK.value: ModeratorMessageChunkEvent,
        DebateEventType.MODERATOR_MESSAGE_COMPLETE.value: ModeratorMessageCompleteEvent,
        DebateEventType.DEBATE_COMPLETE.value: DebateCompleteEvent,
        DebateEventType.ERROR.value: DebateErrorEvent,
        DebateEventType.WARNING.value: DebateWarningEvent,
    }
    
    event_class = event_map.get(event_type, CustomEvent)
    
    # Filter data to only include fields the event class accepts
    if hasattr(event_class, '__dataclass_fields__'):
        valid_fields = set(event_class.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return event_class(**filtered_data)
    
    return event_class()

