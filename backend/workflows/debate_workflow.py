"""
Debate Workflow

"""

import sys
import os
from typing import Dict, Any, Generator, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from workflows.config import (
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
                prop_gen = proposition_turn(self.state)
                try:
                    while True:
                        event = next(prop_gen)
                        yield event
                        self.events.append(event)
                except StopIteration as e:
                    self.state = e.value if e.value else self.state
                # --- Opposition Turn ---
                opp_gen = opposition_turn(self.state)
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











