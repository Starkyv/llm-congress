"""
Debate Workflow

Main workflow class that orchestrates the entire debate simulation.
Uses Agno's Workflow pattern for structured, deterministic execution.

Based on Agno Workflow documentation:
https://docs.agno.com/basics/workflows/overview
"""

import sys
import os
from typing import Dict, Any, Generator, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.workflow import Workflow
# from agno.workflow.step import Step
# from agno.run import RunContext

from workflows.config import (
    DebateWorkflowConfig,
    DebateEvent,
    DebateEventType,
    WORKFLOW_NAME,
    WORKFLOW_VERSION,
)
from workflows.steps.initialize import initialize_debate, get_agent_by_id
from workflows.steps.debate_turn import proposition_turn, opposition_turn, check_round_completion
from workflows.steps.voting import conduct_voting
from workflows.steps.agent_switch import handle_agent_switch
from workflows.steps.conclude import conclude_debate
from state import update_timer, set_phase, set_error
from utils.state_helpers import format_time_elapsed, format_time_remaining


class DebateWorkflow:
    """
    Main debate workflow orchestrator.
    
    This class manages the complete debate lifecycle:
    1. Initialize debate environment
    2. Run debate loop (proposition/opposition turns)
    3. Conduct voting rounds
    4. Handle agent switches
    5. Generate conclusion
    
    Usage:
        workflow = DebateWorkflow()
        
        # Run with streaming events
        for event in workflow.run(topic="UBI should be implemented", duration=300):
            print(event)
        
        # Or run and get final state
        final_state = workflow.run_sync(topic="UBI", duration=300)
    """
    
    def __init__(self):
        self.name = WORKFLOW_NAME
        self.version = WORKFLOW_VERSION
        self.state: Dict[str, Any] = {}
        self.events: List[DebateEvent] = []
        self.is_running = False
    
    def run(
        self,
        topic: str,
        duration: int = 300,
        exchanges_per_round: int = 3,
        first_agent_id: Optional[str] = None,
        stream: bool = True
    ) -> Generator[DebateEvent, None, Dict[str, Any]]:
        """
        Run the debate workflow with streaming events.
        
        Args:
            topic: The debate topic
            duration: Duration in seconds
            exchanges_per_round: Exchanges before voting
            first_agent_id: Optional first agent ID
            stream: Enable streaming
            
        Yields:
            DebateEvent objects
            
        Returns:
            Final debate state
        """
        self.is_running = True
        self.events = []
        
        try:
            # === Step 1: Initialize ===
            self.state, start_event = initialize_debate(
                topic=topic,
                duration=duration,
                exchanges_per_round=exchanges_per_round,
                first_agent_id=first_agent_id
            )
            
            yield start_event
            self.events.append(start_event)
            
            # === Step 2: Main Debate Loop ===
            timer_status = "continue"
            
            while timer_status == "continue" and self.is_running:
                # Update timer
                self.state = update_timer(self.state)
                
                # Emit timer update
                elapsed = self.state.get("elapsed_seconds", 0)
                remaining = duration - elapsed
                
                yield DebateEvent(
                    event_type=DebateEventType.TIMER_UPDATE,
                    data={
                        "elapsed": elapsed,
                        "remaining": max(0, remaining),
                        "elapsed_formatted": format_time_elapsed(elapsed),
                        "remaining_formatted": format_time_remaining(elapsed, duration),
                    },
                    timestamp=datetime.now().isoformat()
                )
                
                # Check if time expired
                if remaining <= 0:
                    timer_status = "expired"
                    break
                
                # --- Proposition Turn ---
                prop_gen = proposition_turn(self.state, stream=stream)
                try:
                    while True:
                        event = next(prop_gen)
                        yield event
                        self.events.append(event)
                except StopIteration as e:
                    self.state = e.value if e.value else self.state
                
                # --- Opposition Turn ---
                opp_gen = opposition_turn(self.state, stream=stream)
                try:
                    while True:
                        event = next(opp_gen)
                        yield event
                        self.events.append(event)
                except StopIteration as e:
                    self.state = e.value if e.value else self.state
                
                # --- Check Round Completion ---
                round_status = check_round_completion(self.state)
                
                if round_status == "time_expired":
                    timer_status = "expired"
                    break
                
                elif round_status == "vote":
                    # --- Voting Phase ---
                    vote_gen = conduct_voting(self.state)
                    decision = "stay"
                    try:
                        while True:
                            event = next(vote_gen)
                            yield event
                            self.events.append(event)
                    except StopIteration as e:
                        if e.value:
                            self.state, decision = e.value
                    
                    # --- Handle Agent Switch ---
                    switch_gen = handle_agent_switch(self.state, decision)
                    try:
                        while True:
                            event = next(switch_gen)
                            yield event
                            self.events.append(event)
                    except StopIteration as e:
                        self.state = e.value if e.value else self.state
                
                # Update timer again
                self.state = update_timer(self.state)
                elapsed = self.state.get("elapsed_seconds", 0)
                if elapsed >= duration:
                    timer_status = "expired"
            
            # === Step 3: Conclusion ===
            conclude_gen = conclude_debate(self.state, stream=stream)
            try:
                while True:
                    event = next(conclude_gen)
                    yield event
                    self.events.append(event)
            except StopIteration as e:
                self.state = e.value if e.value else self.state
            
        except Exception as e:
            # Critical error handling
            error_event = DebateEvent(
                event_type=DebateEventType.ERROR,
                data={
                    "step": "workflow",
                    "error": str(e),
                    "critical": True,
                },
                timestamp=datetime.now().isoformat()
            )
            yield error_event
            self.events.append(error_event)
            
            # Set error state
            if self.state:
                self.state = set_error(self.state, str(e))
        
        finally:
            self.is_running = False
        
        return self.state
    
    def run_sync(
        self,
        topic: str,
        duration: int = 300,
        exchanges_per_round: int = 3,
        first_agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the workflow synchronously without streaming.
        
        Args:
            topic: The debate topic
            duration: Duration in seconds
            exchanges_per_round: Exchanges before voting
            first_agent_id: Optional first agent ID
            
        Returns:
            Final debate state
        """
        # Consume all events
        gen = self.run(
            topic=topic,
            duration=duration,
            exchanges_per_round=exchanges_per_round,
            first_agent_id=first_agent_id,
            stream=False
        )
        
        final_state = None
        try:
            while True:
                event = next(gen)
                # Events are collected in self.events
        except StopIteration as e:
            final_state = e.value
        
        return final_state or self.state
    
    def stop(self):
        """Stop the running workflow gracefully."""
        self.is_running = False
    
    def get_events(self) -> List[DebateEvent]:
        """Get all events emitted during the workflow."""
        return self.events
    
    def get_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return self.state


def create_debate_workflow() -> DebateWorkflow:
    """Factory function to create a new debate workflow."""
    return DebateWorkflow()


# =============================================================================
# Agno Workflow Integration
# =============================================================================
# 
# The following implements a proper Agno Workflow using the steps=[] pattern
# as documented at: https://docs.agno.com/basics/workflows/overview
#
# Agno Workflows support three types of steps:
#   1. Agent - Individual AI agents
#   2. Team - Coordinated groups of agents
#   3. Function - Custom Python functions for orchestration logic
#
# Step functions receive:
#   - step_input: StepInput object with previous_step_content, input, etc.
#   - session_state: Dict (auto-injected if parameter name matches)
#
# Since the debate requires loops and conditionals, we use functions as steps.
# =============================================================================

from agno.workflow import StepInput


def step_initialize(step_input: StepInput, session_state: Dict[str, Any] = None) -> str:
    """
    Step 1: Initialize the debate environment.
    
    This is the first step in the Agno workflow. It sets up the debate state
    and returns a prompt for the first debater.
    
    Args:
        step_input: Agno StepInput with input and previous step data
        session_state: Shared workflow state (auto-injected by Agno)
        
    Returns:
        Initial prompt for the debate
    """
    # Mark debate as started
    if session_state:
        session_state["phase"] = "debating"
        session_state["status"] = "running"
    
    topic = session_state.get("topic", "Unknown topic") if session_state else "Unknown topic"
    
    return f"Debate initialized. Topic: {topic}. The proposition team will begin."


def step_proposition_turn(step_input: StepInput, session_state: Dict[str, Any] = None) -> str:
    """
    Step 2: Execute a proposition agent's turn.
    
    Gets the active proposition agent and generates their argument.
    
    Args:
        step_input: Agno StepInput with input and previous step data
        session_state: Shared workflow state
        
    Returns:
        The proposition agent's argument
    """
    from tasks import get_debate_task
    
    if not session_state:
        return "[Error: No session state available]"
    
    # Get active proposition agent
    active_id = session_state.get("active_proposition_id")
    agent = get_agent_by_id(active_id)
    
    if not agent:
        return f"[Error: Could not find agent with ID: {active_id}]"
    
    # Build context
    topic = session_state.get("topic", "")
    messages = session_state.get("messages", [])
    
    # Get opponent's last argument
    opponent_last = None
    for msg in reversed(messages):
        if msg.get("role") == "opposition":
            opponent_last = msg.get("content")
            break
    
    # Create debate task
    task = get_debate_task(
        topic=topic,
        stance="for",
        debate_history=[
            {"speaker": m.get("agent_name"), "argument": m.get("content")}
            for m in messages[-5:]
        ],
        opponent_last_argument=opponent_last,
        personality_note=getattr(agent, 'personality_type', 'analytical')
    )
    
    # Get response from agent
    response = agent.run(task.build_prompt())
    content = response.content if response else "[No response]"
    
    # Update session state with new message
    from datetime import datetime
    new_message = {
        "agent_id": active_id,
        "agent_name": agent.name,
        "role": "proposition",
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "round_number": session_state.get("current_round", 1)
    }
    session_state.setdefault("messages", []).append(new_message)
    session_state["current_exchange"] = session_state.get("current_exchange", 0) + 1
    
    return content


def step_opposition_turn(step_input: StepInput, session_state: Dict[str, Any] = None) -> str:
    """
    Step 3: Execute the opposition agent's turn.
    
    Gets the opposition agent and generates their counter-argument.
    
    Args:
        step_input: Agno StepInput with input and previous step data
        session_state: Shared workflow state
        
    Returns:
        The opposition agent's argument
    """
    from tasks import get_debate_task
    
    if not session_state:
        return "[Error: No session state available]"
    
    # Get opposition agent
    opposition_id = session_state.get("opposition_id")
    agent = get_agent_by_id(opposition_id)
    
    if not agent:
        return f"[Error: Could not find opposition agent with ID: {opposition_id}]"
    
    # Build context
    topic = session_state.get("topic", "")
    messages = session_state.get("messages", [])
    
    # The proposition's argument is from the previous step
    opponent_last = step_input.previous_step_content
    
    # Create debate task
    task = get_debate_task(
        topic=topic,
        stance="against",
        debate_history=[
            {"speaker": m.get("agent_name"), "argument": m.get("content")}
            for m in messages[-5:]
        ],
        opponent_last_argument=opponent_last,
        personality_note=getattr(agent, 'personality_type', 'skeptical')
    )
    
    # Get response from agent
    response = agent.run(task.build_prompt())
    content = response.content if response else "[No response]"
    
    # Update session state with new message
    from datetime import datetime
    new_message = {
        "agent_id": opposition_id,
        "agent_name": agent.name,
        "role": "opposition",
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "round_number": session_state.get("current_round", 1)
    }
    session_state.setdefault("messages", []).append(new_message)
    
    return content


def step_check_and_vote(step_input: StepInput, session_state: Dict[str, Any] = None) -> str:
    """
    Step 4: Check if voting should occur and conduct if needed.
    
    This step checks exchange count and conducts voting when threshold is reached.
    
    Args:
        step_input: Agno StepInput with input and previous step data
        session_state: Shared workflow state
        
    Returns:
        Voting result or continue signal
    """
    from tasks import get_vote_task, VoteEvaluationTask
    
    if not session_state:
        return "continue"
    
    exchanges_per_round = session_state.get("exchanges_per_round", 3)
    current_exchange = session_state.get("current_exchange", 0)
    
    # Check if voting should trigger
    if current_exchange < exchanges_per_round:
        return "continue"
    
    # Conduct voting
    active_id = session_state.get("active_proposition_id")
    active_agent = get_agent_by_id(active_id)
    active_name = active_agent.name if active_agent else "Unknown"
    
    # Get observers (other proposition agents)
    observer_ids = session_state.get("observer_ids", [])
    messages = session_state.get("messages", [])
    
    # Prepare recent exchanges for voting context
    recent_exchanges = [
        {"speaker": m.get("agent_name"), "argument": m.get("content")}
        for m in messages[-6:]
    ]
    
    # Collect votes
    votes = {"in": 0, "out": 0}
    vote_records = []
    
    for observer_id in observer_ids:
        observer = get_agent_by_id(observer_id)
        if not observer:
            continue
        
        vote_task = get_vote_task(
            current_debater_name=active_name,
            recent_exchanges=recent_exchanges,
            evaluation_criteria="argument strength, evidence quality, persuasiveness",
            voter_personality=getattr(observer, 'personality_type', 'neutral')
        )
        
        try:
            response = observer.run(vote_task.build_prompt())
            raw_response = response.content if response else ""
            vote_result = VoteEvaluationTask.parse_vote_response(raw_response)
            
            if vote_result:
                votes[vote_result.vote] = votes.get(vote_result.vote, 0) + 1
                vote_records.append({
                    "voter": observer.name,
                    "vote": vote_result.vote,
                    "reasoning": vote_result.reasoning
                })
        except Exception:
            votes["in"] += 1  # Default to "in" on error
    
    # Update session state
    session_state["vote_tally"] = votes
    session_state["current_votes"] = vote_records
    
    # Determine decision
    decision = "switch" if votes.get("out", 0) > votes.get("in", 0) else "stay"
    
    # Handle agent switch if needed
    if decision == "switch":
        # Find replacement
        all_prop_ids = session_state.get("all_proposition_ids", [])
        available = [aid for aid in all_prop_ids if aid != active_id and aid in observer_ids]
        
        if available:
            import random
            new_id = random.choice(available)
            new_agent = get_agent_by_id(new_id)
            
            # Record switch
            from datetime import datetime
            switch_record = {
                "old_agent_id": active_id,
                "old_agent_name": active_name,
                "new_agent_id": new_id,
                "new_agent_name": new_agent.name if new_agent else "Unknown",
                "vote_tally": votes,
                "round_number": session_state.get("current_round", 1),
                "timestamp": datetime.now().isoformat()
            }
            session_state.setdefault("agent_switches", []).append(switch_record)
            
            # Update active agent
            session_state["active_proposition_id"] = new_id
            
            # Update observers
            session_state["observer_ids"] = [
                aid for aid in all_prop_ids if aid != new_id
            ]
            
            decision = f"switched:{active_name}->{new_agent.name if new_agent else 'Unknown'}"
    
    # Reset for next round
    session_state["current_exchange"] = 0
    session_state["current_round"] = session_state.get("current_round", 1) + 1
    session_state["current_votes"] = []
    session_state["vote_tally"] = {"in": 0, "out": 0}
    
    return decision


def step_conclude(step_input: StepInput, session_state: Dict[str, Any] = None) -> str:
    """
    Step 5: Generate final summary and conclude the debate.
    
    Uses the moderator agent to create a comprehensive summary.
    
    Args:
        step_input: Agno StepInput with input and previous step data
        session_state: Shared workflow state
        
    Returns:
        Final debate summary
    """
    from tasks import get_moderate_task
    from agents import get_moderator_agent
    
    if not session_state:
        return "[Error: No session state available]"
    
    # Set phase to concluding
    session_state["phase"] = "concluding"
    
    # Get messages from session_state
    messages = session_state.get("messages", [])
    
    # Build transcript as list of dicts (required format for get_moderate_task)
    transcript_list = []
    for m in messages:
        if isinstance(m, dict):
            transcript_list.append({
                "speaker": m.get("agent_name", "Unknown"),
                "role": m.get("role", "unknown"),
                "content": m.get("content", "")
            })
    
    # Build vote history as list of dicts
    # Note: The current_votes contains voter info, agent_switches contains switch info
    vote_list = []
    current_votes = session_state.get("current_votes", [])
    for v in current_votes:
        if isinstance(v, dict):
            vote_list.append({
                "voter": v.get("voter", "Unknown"),
                "voted_for": session_state.get("active_proposition_id", "Unknown"),
                "vote_type": v.get("vote", "in"),
                "reasoning": v.get("reasoning", "")
            })
    
    # Create moderation task
    topic = session_state.get("topic", "")
    duration = session_state.get("elapsed_seconds", 0)
    
    mod_task = get_moderate_task(
        topic=topic,
        full_debate_transcript=transcript_list,
        vote_history=vote_list,
        duration_seconds=duration
    )
    
    # Get moderator
    moderator = get_moderator_agent()
    
    try:
        response = moderator.run(mod_task.build_prompt())
        summary = response.content if response else "[Could not generate summary]"
    except Exception as e:
        summary = f"Debate on '{topic}' concluded after {len(messages)} exchanges."
    
    # Set final state
    session_state["phase"] = "completed"
    session_state["status"] = "completed"
    session_state["summary"] = summary
    
    return summary


def create_agno_workflow(
    topic: str,
    duration: int = 300,
    exchanges_per_round: int = 3
) -> Workflow:
    """
    Create an Agno Workflow instance for the debate.
    
    This creates a workflow compatible with Agno's workflow system,
    using session_state for state management and properly wired steps.
    
    According to Agno docs (https://docs.agno.com/basics/workflows/overview):
    - Workflows orchestrate agents, teams, and functions in steps
    - Output flows automatically from one step to the next
    - session_state provides shared state across all steps
    
    Args:
        topic: The debate topic
        duration: Duration in seconds
        exchanges_per_round: Exchanges before voting
        
    Returns:
        Agno Workflow instance with steps configured
    """
    from state import initialize_state
    from agents import (
        get_all_proposition_agents,
        get_opposition_agent,
        select_random_proposition,
    )
    
    # Get agents
    proposition_agents = get_all_proposition_agents()
    opposition_agent = get_opposition_agent()
    first_agent = select_random_proposition()
    
    # Get observer IDs (all proposition agents except active one)
    all_prop_ids = [a.agent_id for a in proposition_agents]
    observer_ids = [aid for aid in all_prop_ids if aid != first_agent.agent_id]
    
    # Create initial state
    initial_state = initialize_state(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges_per_round,
        all_proposition_ids=all_prop_ids,
        opposition_id=opposition_agent.agent_id,
        active_proposition_id=first_agent.agent_id,
        observer_ids=observer_ids
    )
    
    # Create Agno workflow with steps
    # Steps execute in order: init -> proposition -> opposition -> vote -> conclude
    workflow = Workflow(
        name=WORKFLOW_NAME,
        description="Multi-agent debate simulation with voting and agent switching",
        session_state=initial_state,
        steps=[
            step_initialize,
            step_proposition_turn,
            step_opposition_turn,
            step_check_and_vote,
            step_conclude,
        ],
    )
    
    return workflow


def create_debate_loop_workflow(
    topic: str,
    duration: int = 300,
    exchanges_per_round: int = 3,
    max_rounds: int = 5
) -> Workflow:
    """
    Create an Agno Workflow that runs multiple debate rounds.
    
    For debates requiring multiple exchanges before conclusion, this workflow
    runs the proposition/opposition/voting cycle multiple times.
    
    Args:
        topic: The debate topic
        duration: Duration in seconds
        exchanges_per_round: Exchanges before voting
        max_rounds: Maximum number of full debate rounds
        
    Returns:
        Agno Workflow instance with repeated debate steps
    """
    from state import initialize_state
    from agents import (
        get_all_proposition_agents,
        get_opposition_agent,
        select_random_proposition,
    )
    
    # Get agents
    proposition_agents = get_all_proposition_agents()
    opposition_agent = get_opposition_agent()
    first_agent = select_random_proposition()
    
    # Get observer IDs
    all_prop_ids = [a.agent_id for a in proposition_agents]
    observer_ids = [aid for aid in all_prop_ids if aid != first_agent.agent_id]
    
    # Create initial state
    initial_state = initialize_state(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges_per_round,
        all_proposition_ids=all_prop_ids,
        opposition_id=opposition_agent.agent_id,
        active_proposition_id=first_agent.agent_id,
        observer_ids=observer_ids
    )
    
    # Build steps list with repeated debate cycles
    # Each round: proposition -> opposition (repeated exchanges_per_round times)
    # Then voting, then repeat for max_rounds
    steps = [step_initialize]
    
    for round_num in range(max_rounds):
        for exchange in range(exchanges_per_round):
            steps.append(step_proposition_turn)
            steps.append(step_opposition_turn)
        steps.append(step_check_and_vote)
    
    steps.append(step_conclude)
    
    # Create workflow
    workflow = Workflow(
        name=f"{WORKFLOW_NAME} - {max_rounds} Rounds",
        description=f"Multi-agent debate with {max_rounds} voting rounds",
        session_state=initial_state,
        steps=steps,
    )
    
    return workflow

