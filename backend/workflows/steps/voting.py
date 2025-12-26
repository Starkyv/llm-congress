"""
Voting Step

Handles the voting phase where observers evaluate the active debater.
"""

import sys
import os
from typing import Dict, Any, List, Tuple, Generator
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state import start_voting_round, add_vote, complete_voting_round
from tasks import get_vote_task, VoteEvaluationTask
from utils.state_queries import get_recent_history
from workflows.config import DebateEvent, DebateEventType
from workflows.steps.initialize import get_agent_by_id


def conduct_voting(
    state: Dict[str, Any]
) -> Generator[DebateEvent, None, Tuple[Dict[str, Any], str]]:
    """
    Conduct a voting round.
    
    Args:
        state: Current debate state
        
    Yields:
        DebateEvent objects for streaming
        
    Returns:
        Tuple of (updated state, decision: "switch" or "stay")
    """
    # Get the active proposition agent being evaluated
    active_id = state.get("active_proposition_id")
    active_agent = get_agent_by_id(active_id)
    active_name = active_agent.name if active_agent else "Unknown"
    
    # Start voting round in state
    state = start_voting_round(state, active_id)
    
    # Emit voting initiated event
    yield DebateEvent(
        event_type=DebateEventType.VOTING_INITIATED,
        data={
            "evaluating_agent_id": active_id,
            "evaluating_agent_name": active_name,
            "round_number": state.get("current_round", 1),
            "observer_count": len(state.get("observer_ids", [])),
        },
        timestamp=datetime.now().isoformat()
    )
    
    # Get recent exchanges for context
    recent = get_recent_history(state, n=6)
    recent_exchanges = [
        {"speaker": m.get("agent_name"), "argument": m.get("content")}
        for m in recent
    ]
    
    # Get observers
    observer_ids = state.get("observer_ids", [])
    
    # Collect votes from each observer
    votes = []
    for observer_id in observer_ids:
        observer_agent = get_agent_by_id(observer_id)
        if not observer_agent:
            continue
        
        # Create vote task
        vote_task = get_vote_task(
            current_debater_name=active_name,
            recent_exchanges=recent_exchanges,
            evaluation_criteria="argument strength, evidence quality, persuasiveness, and response to opponent",
            voter_personality=observer_agent.personality_type
        )
        
        # Get vote from observer (stream=False for RunOutput with .content)
        try:
            prompt = vote_task.build_prompt()
            response = observer_agent.run(prompt, stream=False)
            raw_response = response.content if response else ""
            
            # Parse vote
            vote_result = VoteEvaluationTask.parse_vote_response(raw_response)
            
            if vote_result:
                # Add vote to state
                state = add_vote(
                    state,
                    voter_id=observer_id,
                    voter_name=observer_agent.name,
                    vote=vote_result.vote,
                    reasoning=vote_result.reasoning
                )
                
                votes.append({
                    "voter_id": observer_id,
                    "voter_name": observer_agent.name,
                    "vote": vote_result.vote,
                    "reasoning": vote_result.reasoning
                })
                
                # Emit vote cast event
                yield DebateEvent(
                    event_type=DebateEventType.VOTE_CAST,
                    data={
                        "voter_id": observer_id,
                        "voter_name": observer_agent.name,
                        "vote": vote_result.vote,
                        "reasoning": vote_result.reasoning,
                    },
                    timestamp=datetime.now().isoformat()
                )
            else:
                # Default to "in" if parsing fails
                state = add_vote(
                    state,
                    voter_id=observer_id,
                    voter_name=observer_agent.name,
                    vote="in",
                    reasoning="[Vote could not be parsed, defaulting to 'in']"
                )
                
                yield DebateEvent(
                    event_type=DebateEventType.WARNING,
                    data={
                        "message": f"Could not parse vote from {observer_agent.name}, defaulting to 'in'",
                        "voter_id": observer_id,
                    },
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            # Default to "in" on error
            state = add_vote(
                state,
                voter_id=observer_id,
                voter_name=observer_agent.name,
                vote="in",
                reasoning=f"[Error during voting: {str(e)[:50]}]"
            )
            
            yield DebateEvent(
                event_type=DebateEventType.ERROR,
                data={
                    "step": "voting",
                    "error": str(e),
                    "voter_id": observer_id,
                },
                timestamp=datetime.now().isoformat()
            )
    
    # Complete voting round
    state, decision = complete_voting_round(state)
    
    # Emit voting complete event
    yield DebateEvent(
        event_type=DebateEventType.VOTING_COMPLETE,
        data={
            "evaluating_agent_id": active_id,
            "evaluating_agent_name": active_name,
            "vote_tally": state.get("vote_tally", {}),
            "decision": decision,
            "votes": votes,
        },
        timestamp=datetime.now().isoformat()
    )
    
    return state, decision


def process_votes(raw_votes: List[str]) -> List[Dict[str, Any]]:
    """
    Process raw vote responses into structured votes.
    
    Args:
        raw_votes: List of raw vote response strings
        
    Returns:
        List of parsed vote dicts
    """
    parsed = []
    for raw in raw_votes:
        result = VoteEvaluationTask.parse_vote_response(raw)
        if result:
            parsed.append({
                "vote": result.vote,
                "reasoning": result.reasoning
            })
        else:
            # Default to "in" if parsing fails
            parsed.append({
                "vote": "in",
                "reasoning": "[Could not parse vote]"
            })
    return parsed

