"""
Tasks Module

Provides reusable task templates for debate, voting, and moderation.
"""

from .debate_task import (
    DebateArgumentTask,
    DebateContext,
    create_debate_task,
)
from .vote_task import (
    VoteEvaluationTask,
    VoteResult,
    DebateExchange,
    create_vote_task,
)
from .moderate_task import (
    ModerateSummaryTask,
    DebateMessage,
    VoteEvent,
    create_moderate_task,
)


def get_debate_task(
    topic: str,
    stance: str,
    debate_history: list = None,
    opponent_last_argument: str = None,
    personality_note: str = "analytical"
) -> DebateArgumentTask:
    """
    Get a debate argument task.
    
    Args:
        topic: The debate topic
        stance: 'for' or 'against'
        debate_history: Previous exchanges
        opponent_last_argument: Opponent's last argument
        personality_note: Agent's personality style
        
    Returns:
        DebateArgumentTask instance
    """
    return create_debate_task(
        topic=topic,
        stance=stance,
        debate_history=debate_history,
        opponent_last_argument=opponent_last_argument,
        personality_note=personality_note
    )


def get_vote_task(
    current_debater_name: str,
    recent_exchanges: list = None,
    evaluation_criteria: str = None,
    voter_personality: str = "analytical"
) -> VoteEvaluationTask:
    """
    Get a vote evaluation task.
    
    Args:
        current_debater_name: Name of debater being evaluated
        recent_exchanges: Recent debate exchanges
        evaluation_criteria: What to evaluate
        voter_personality: Voter's personality type
        
    Returns:
        VoteEvaluationTask instance
    """
    return create_vote_task(
        current_debater_name=current_debater_name,
        recent_exchanges=recent_exchanges,
        evaluation_criteria=evaluation_criteria,
        voter_personality=voter_personality
    )


def get_moderate_task(
    topic: str,
    full_debate_transcript: list = None,
    vote_history: list = None,
    duration_seconds: int = 0
) -> ModerateSummaryTask:
    """
    Get a moderation summary task.
    
    Args:
        topic: The debate topic
        full_debate_transcript: Complete debate transcript
        vote_history: All votes that occurred
        duration_seconds: Total debate duration
        
    Returns:
        ModerateSummaryTask instance
    """
    return create_moderate_task(
        topic=topic,
        full_debate_transcript=full_debate_transcript,
        vote_history=vote_history,
        duration_seconds=duration_seconds
    )


__all__ = [
    # Task classes
    'DebateArgumentTask',
    'VoteEvaluationTask',
    'ModerateSummaryTask',
    # Data models
    'DebateContext',
    'DebateExchange',
    'DebateMessage',
    'VoteResult',
    'VoteEvent',
    # Factory functions
    'get_debate_task',
    'get_vote_task',
    'get_moderate_task',
    'create_debate_task',
    'create_vote_task',
    'create_moderate_task',
]

