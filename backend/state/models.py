"""
Debate State Models

Pydantic models for managing debate state with Agno Workflows.
These models integrate with Agno's session_state system for automatic
persistence across workflow steps.
"""

from datetime import datetime
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, computed_field


class Message(BaseModel):
    """A single debate message/argument"""
    agent_id: str = Field(..., description="Unique ID of the speaking agent")
    agent_name: str = Field(..., description="Display name of the agent")
    role: Literal["proposition", "opposition"] = Field(..., description="Debate role")
    content: str = Field(..., description="The argument content")
    timestamp: datetime = Field(default_factory=datetime.now, description="When message was created")
    round_number: int = Field(..., description="Which debate round this belongs to")
    
    @computed_field
    @property
    def word_count(self) -> int:
        """Calculate word count of the message content"""
        return len(self.content.split())


class Vote(BaseModel):
    """A single vote from an observer agent"""
    voter_id: str = Field(..., description="ID of the voting agent")
    voter_name: str = Field(..., description="Name of the voting agent")
    evaluating_agent_id: str = Field(..., description="ID of agent being evaluated")
    vote: Literal["in", "out"] = Field(..., description="Vote decision")
    reasoning: str = Field(..., description="Explanation for the vote")
    timestamp: datetime = Field(default_factory=datetime.now, description="When vote was cast")
    round_number: int = Field(..., description="Which round this vote belongs to")


class AgentSwitch(BaseModel):
    """Record of a proposition agent switch"""
    old_agent_id: str = Field(..., description="ID of agent being replaced")
    old_agent_name: str = Field(..., description="Name of agent being replaced")
    new_agent_id: str = Field(..., description="ID of replacement agent")
    new_agent_name: str = Field(..., description="Name of replacement agent")
    reason: str = Field(..., description="Why the switch occurred")
    vote_tally: Dict[str, int] = Field(..., description="Vote counts that caused switch")
    round_number: int = Field(..., description="Round when switch occurred")
    timestamp: datetime = Field(default_factory=datetime.now, description="When switch happened")


class DebateState(BaseModel):
    """
    Main state model for the entire debate.
    
    This model is used with Agno's Workflow session_state system.
    All workflow steps can access and modify this state automatically.
    
    Usage with Agno Workflow:
        workflow = Workflow(
            name="Debate",
            session_state=DebateState(...).model_dump(),
            steps=[...]
        )
    """
    
    # === Configuration State (set once at start) ===
    topic: str = Field(..., description="The debate topic/proposition")
    duration: int = Field(default=300, description="Total debate duration in seconds")
    exchanges_per_round: int = Field(default=3, description="Exchanges before voting")
    
    # === Agent Tracking State ===
    active_proposition_id: str = Field(..., description="Currently active proposition agent")
    opposition_id: str = Field(..., description="Opposition agent ID")
    observer_ids: List[str] = Field(default_factory=list, description="IDs of observing agents")
    all_proposition_ids: List[str] = Field(default_factory=list, description="All proposition agent IDs")
    
    # === Debate History State ===
    messages: List[Message] = Field(default_factory=list, description="All debate messages")
    current_round: int = Field(default=1, description="Current round number")
    current_exchange: int = Field(default=0, description="Exchange count in current round")
    
    # === Voting State ===
    current_votes: List[Vote] = Field(default_factory=list, description="Votes in current round")
    vote_tally: Dict[str, int] = Field(
        default_factory=lambda: {"in": 0, "out": 0},
        description="Current vote counts"
    )
    evaluating_agent_id: Optional[str] = Field(default=None, description="Agent being evaluated")
    
    # === Switch History State ===
    agent_switches: List[AgentSwitch] = Field(
        default_factory=list,
        description="History of agent switches"
    )
    
    # === Timer State ===
    start_time: datetime = Field(default_factory=datetime.now, description="When debate started")
    elapsed_seconds: int = Field(default=0, description="Total elapsed time")
    paused_seconds: int = Field(default=0, description="Time paused during voting")
    is_paused: bool = Field(default=False, description="Whether timer is paused")
    
    # === Phase State ===
    phase: Literal["initializing", "debating", "voting", "concluding", "completed"] = Field(
        default="initializing",
        description="Current debate phase"
    )
    status: Literal["running", "paused", "completed", "error"] = Field(
        default="running",
        description="Overall debate status"
    )
    error_message: Optional[str] = Field(default=None, description="Error message if status is error")
    
    # === Computed Properties ===
    @computed_field
    @property
    def total_messages(self) -> int:
        """Total number of messages in the debate"""
        return len(self.messages)
    
    @computed_field
    @property
    def total_switches(self) -> int:
        """Total number of agent switches"""
        return len(self.agent_switches)
    
    @computed_field
    @property
    def is_time_up(self) -> bool:
        """Check if debate duration has been reached"""
        return self.elapsed_seconds >= self.duration
    
    def model_dump_for_workflow(self) -> dict:
        """
        Convert to dict suitable for Agno workflow session_state.
        Handles datetime serialization.
        """
        return self.model_dump(mode='json')


# Type alias for session state dict
DebateStateDict = Dict[str, any]

