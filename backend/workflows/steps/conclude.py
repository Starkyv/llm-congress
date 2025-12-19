"""
Conclude Step

Generates final summary using the moderator agent.
"""

import sys
import os
from typing import Dict, Any, Generator
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state import set_phase
from tasks import get_moderate_task
from agents import get_moderator_agent
from utils.state_queries import get_statistics, get_full_transcript, get_vote_history
from workflows.config import DebateEvent, DebateEventType


def conclude_debate(
    state: Dict[str, Any],
    stream: bool = True
) -> Generator[DebateEvent, None, Dict[str, Any]]:
    """
    Generate final summary and conclude the debate.
    
    Args:
        state: Current debate state
        stream: Whether to stream response
        
    Yields:
        DebateEvent objects for streaming
        
    Returns:
        Updated state with summary
    """
    # Set phase to concluding
    state = set_phase(state, "concluding")
    
    yield DebateEvent(
        event_type=DebateEventType.PHASE_CHANGE,
        data={
            "phase": "concluding",
            "message": "Debate concluding, generating summary...",
        },
        timestamp=datetime.now().isoformat()
    )
    
    # Calculate statistics
    stats = get_statistics(state)
    
    # Get full transcript
    transcript = get_full_transcript(state)
    
    # Get vote history
    vote_history = get_vote_history(state)
    
    # Create moderation task
    topic = state.get("topic", "")
    duration = state.get("elapsed_seconds", 0)
    
    mod_task = get_moderate_task(
        topic=topic,
        full_debate_transcript=transcript,
        vote_history=vote_history,
        duration_seconds=duration
    )
    
    # Get moderator agent
    moderator = get_moderator_agent()
    
    # Generate summary
    summary = ""
    try:
        prompt = mod_task.build_prompt()
        response = moderator.run(prompt)
        summary = response.content if response else ""
        
        # Emit chunks for streaming effect
        if stream and summary:
            words = summary.split()
            chunk_size = 8
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                yield DebateEvent(
                    event_type=DebateEventType.MODERATOR_MESSAGE_CHUNK,
                    data={
                        "chunk": chunk,
                    },
                    timestamp=datetime.now().isoformat()
                )
        
        # Emit completion
        yield DebateEvent(
            event_type=DebateEventType.MODERATOR_MESSAGE_COMPLETE,
            data={
                "summary": summary,
                "word_count": len(summary.split()) if summary else 0,
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        # Generate simple fallback summary
        yield DebateEvent(
            event_type=DebateEventType.ERROR,
            data={
                "step": "conclude",
                "error": str(e),
            },
            timestamp=datetime.now().isoformat()
        )
        
        summary = generate_fallback_summary(state, stats)
        
        yield DebateEvent(
            event_type=DebateEventType.MODERATOR_MESSAGE_COMPLETE,
            data={
                "summary": summary,
                "is_fallback": True,
            },
            timestamp=datetime.now().isoformat()
        )
    
    # Set phase to completed
    state = set_phase(state, "completed")
    state["status"] = "completed"
    state["summary"] = summary
    
    # Emit debate complete event
    yield DebateEvent(
        event_type=DebateEventType.DEBATE_COMPLETE,
        data={
            "topic": topic,
            "duration_seconds": duration,
            "statistics": stats,
            "summary_preview": summary[:200] + "..." if len(summary) > 200 else summary,
        },
        timestamp=datetime.now().isoformat()
    )
    
    return state


def generate_fallback_summary(state: Dict[str, Any], stats: Dict[str, Any]) -> str:
    """
    Generate a simple fallback summary if moderator fails.
    
    Args:
        state: Debate state
        stats: Statistics dict
        
    Returns:
        Simple summary string
    """
    topic = state.get("topic", "Unknown topic")
    total_messages = stats.get("total_messages", 0)
    total_rounds = stats.get("total_rounds", 0)
    total_switches = stats.get("total_switches", 0)
    elapsed = stats.get("elapsed_seconds", 0)
    
    minutes = elapsed // 60
    seconds = elapsed % 60
    
    summary = f"""## Debate Summary

**Topic:** {topic}

**Duration:** {minutes} minutes, {seconds} seconds

### Statistics
- Total exchanges: {total_messages}
- Rounds completed: {total_rounds}
- Agent switches: {total_switches}

### Conclusion
This debate covered the topic "{topic}" with {total_messages} total exchanges 
over {total_rounds} round(s). The agents presented various arguments from 
different perspectives.

*[This is an automatically generated summary due to moderator unavailability]*
"""
    
    return summary

