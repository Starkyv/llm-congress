#!/usr/bin/env python3
"""
Comprehensive tests for Checkpoint 4 - Debate State Management

Tests the state models, operations, and integration with Agno workflow patterns.
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from state import (
    # Models
    Message,
    Vote,
    AgentSwitch,
    DebateState,
    # Operations
    initialize_state,
    add_message,
    start_voting_round,
    add_vote,
    complete_voting_round,
    record_agent_switch,
    update_timer,
    set_phase,
    set_error,
    get_available_replacement,
    # Validators
    validate_state_structure,
    validate_phase_transition,
    validate_vote,
    validate_role,
    validate_exchanges_complete,
)
from utils.state_queries import (
    get_recent_history,
    get_recent_history_formatted,
    get_statistics,
    get_full_transcript,
)
from utils.state_helpers import (
    format_time_elapsed,
    should_trigger_voting,
    should_end_debate,
    get_next_speaker_role,
)

console = Console()


def test_message_model():
    """Test Message model creation and validation"""
    console.print("\n[yellow]Test 1: Message Model[/yellow]")
    
    try:
        msg = Message(
            agent_id="prop_analytical",
            agent_name="Analytical Debater",
            role="proposition",
            content="This is a test argument with evidence.",
            round_number=1
        )
        
        assert msg.agent_id == "prop_analytical"
        assert msg.role == "proposition"
        assert msg.word_count == 7  # Computed field
        assert msg.timestamp is not None
        
        console.print("  ✓ Message created successfully")
        console.print(f"    Word count: {msg.word_count}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_vote_model():
    """Test Vote model creation and validation"""
    console.print("\n[yellow]Test 2: Vote Model[/yellow]")
    
    try:
        vote = Vote(
            voter_id="prop_emotional",
            voter_name="Emotional Advocate",
            evaluating_agent_id="prop_analytical",
            vote="in",
            reasoning="Strong data-driven arguments",
            round_number=1
        )
        
        assert vote.vote == "in"
        assert vote.voter_id == "prop_emotional"
        
        console.print("  ✓ Vote created successfully")
        console.print(f"    Vote: {vote.vote}, Reasoning: {vote.reasoning[:30]}...")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_debate_state_model():
    """Test DebateState model creation"""
    console.print("\n[yellow]Test 3: DebateState Model[/yellow]")
    
    try:
        state = DebateState(
            topic="UBI should be implemented",
            duration=300,
            exchanges_per_round=3,
            active_proposition_id="prop_analytical",
            opposition_id="opp_pragmatist",
            observer_ids=["prop_emotional", "prop_rhetorical"],
            all_proposition_ids=["prop_analytical", "prop_emotional", "prop_rhetorical"]
        )
        
        assert state.topic == "UBI should be implemented"
        assert state.total_messages == 0  # Computed field
        assert state.is_time_up == False  # Computed field
        assert state.phase == "initializing"
        
        console.print("  ✓ DebateState created successfully")
        console.print(f"    Topic: {state.topic}")
        console.print(f"    Phase: {state.phase}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_initialize_state():
    """Test state initialization"""
    console.print("\n[yellow]Test 4: Initialize State[/yellow]")
    
    try:
        state = initialize_state(
            topic="Testing topic",
            duration=300,
            exchanges_per_round=3,
            all_proposition_ids=["prop_1", "prop_2", "prop_3"],
            opposition_id="opp_1",
            active_proposition_id="prop_1"
        )
        
        assert state["topic"] == "Testing topic"
        assert state["duration"] == 300
        assert state["phase"] == "initializing"
        assert state["current_round"] == 1
        assert len(state["messages"]) == 0
        assert "prop_2" in state["observer_ids"]
        assert "prop_3" in state["observer_ids"]
        
        console.print("  ✓ State initialized successfully")
        console.print(f"    Observers: {state['observer_ids']}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_add_messages():
    """Test adding messages to state"""
    console.print("\n[yellow]Test 5: Add Messages[/yellow]")
    
    try:
        state = initialize_state(
            topic="Testing",
            duration=300,
            exchanges_per_round=3,
            all_proposition_ids=["prop_1"],
            opposition_id="opp_1",
            active_proposition_id="prop_1"
        )
        
        # Add messages
        state = add_message(state, "prop_1", "Agent 1", "proposition", "First argument")
        state = add_message(state, "opp_1", "Opposition", "opposition", "Counter argument")
        state = add_message(state, "prop_1", "Agent 1", "proposition", "Rebuttal")
        
        assert len(state["messages"]) == 3
        assert state["current_exchange"] == 3
        
        console.print("  ✓ Messages added successfully")
        console.print(f"    Message count: {len(state['messages'])}")
        console.print(f"    Exchange count: {state['current_exchange']}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_voting_flow():
    """Test the complete voting flow"""
    console.print("\n[yellow]Test 6: Voting Flow[/yellow]")
    
    try:
        # Initialize with observers
        state = initialize_state(
            topic="Testing",
            duration=300,
            exchanges_per_round=3,
            all_proposition_ids=["prop_1", "prop_2", "prop_3", "prop_4"],
            opposition_id="opp_1",
            active_proposition_id="prop_1"
        )
        
        # Set phase to debating
        state = set_phase(state, "debating")
        
        # Add some messages
        state = add_message(state, "prop_1", "Agent 1", "proposition", "Argument 1")
        state = add_message(state, "opp_1", "Opposition", "opposition", "Counter 1")
        state = add_message(state, "prop_1", "Agent 1", "proposition", "Argument 2")
        
        # Start voting
        state = start_voting_round(state, "prop_1")
        assert state["phase"] == "voting"
        assert state["is_paused"] == True
        
        # Cast votes (2 in, 1 out - should stay)
        state = add_vote(state, "prop_2", "Agent 2", "in", "Good arguments")
        state = add_vote(state, "prop_3", "Agent 3", "in", "Compelling data")
        state = add_vote(state, "prop_4", "Agent 4", "out", "Could be better")
        
        assert state["vote_tally"]["in"] == 2
        assert state["vote_tally"]["out"] == 1
        
        # Complete voting
        state, decision = complete_voting_round(state)
        
        assert decision == "stay"  # More in votes than out
        assert state["phase"] == "debating"
        assert state["is_paused"] == False
        assert state["current_round"] == 2
        
        console.print("  ✓ Voting flow completed successfully")
        console.print(f"    Vote tally: IN={state['vote_tally']['in']}, OUT={state['vote_tally']['out']}")
        console.print(f"    Decision: {decision}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_agent_switch():
    """Test agent switch recording"""
    console.print("\n[yellow]Test 7: Agent Switch[/yellow]")
    
    try:
        state = initialize_state(
            topic="Testing",
            duration=300,
            exchanges_per_round=3,
            all_proposition_ids=["prop_1", "prop_2", "prop_3"],
            opposition_id="opp_1",
            active_proposition_id="prop_1"
        )
        
        # Record a switch
        state = record_agent_switch(
            state,
            old_agent_id="prop_1",
            old_agent_name="Agent 1",
            new_agent_id="prop_2",
            new_agent_name="Agent 2",
            reason="Voted out by observers"
        )
        
        assert len(state["agent_switches"]) == 1
        assert state["active_proposition_id"] == "prop_2"
        assert "prop_1" in state["observer_ids"]
        assert "prop_2" not in state["observer_ids"]
        
        console.print("  ✓ Agent switch recorded successfully")
        console.print(f"    New active: {state['active_proposition_id']}")
        console.print(f"    Observers: {state['observer_ids']}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_get_recent_history():
    """Test history retrieval"""
    console.print("\n[yellow]Test 8: Get Recent History[/yellow]")
    
    try:
        state = initialize_state(
            topic="Testing",
            duration=300,
            exchanges_per_round=3,
            all_proposition_ids=["prop_1"],
            opposition_id="opp_1",
            active_proposition_id="prop_1"
        )
        
        # Add 10 messages
        for i in range(10):
            role = "proposition" if i % 2 == 0 else "opposition"
            agent = "prop_1" if role == "proposition" else "opp_1"
            state = add_message(state, agent, f"Agent {agent}", role, f"Message {i+1}")
        
        # Get last 3
        recent = get_recent_history(state, 3)
        
        assert len(recent) == 3
        assert "Message 10" in recent[-1]["content"]
        
        # Get formatted
        formatted = get_recent_history_formatted(state, 3)
        assert "Message 10" in formatted
        
        console.print("  ✓ Recent history retrieved successfully")
        console.print(f"    Retrieved {len(recent)} messages")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_statistics():
    """Test statistics calculation"""
    console.print("\n[yellow]Test 9: Statistics[/yellow]")
    
    try:
        state = initialize_state(
            topic="Testing",
            duration=300,
            exchanges_per_round=3,
            all_proposition_ids=["prop_1"],
            opposition_id="opp_1",
            active_proposition_id="prop_1"
        )
        
        # Add messages with varying lengths
        state = add_message(state, "prop_1", "Agent 1", "proposition", 
                          "This is a longer message with many words to test statistics")
        state = add_message(state, "opp_1", "Opposition", "opposition", 
                          "Short reply")
        state = add_message(state, "prop_1", "Agent 1", "proposition", 
                          "Another message")
        
        stats = get_statistics(state)
        
        assert stats["total_messages"] == 3
        assert stats["total_words"] > 0
        assert "average_message_length" in stats
        
        console.print("  ✓ Statistics calculated successfully")
        console.print(f"    Total messages: {stats['total_messages']}")
        console.print(f"    Total words: {stats['total_words']}")
        console.print(f"    Avg length: {stats['average_message_length']} words")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_validators():
    """Test validation functions"""
    console.print("\n[yellow]Test 10: Validators[/yellow]")
    
    try:
        # Test phase transitions
        valid, error = validate_phase_transition("debating", "voting")
        assert valid == True
        
        valid, error = validate_phase_transition("completed", "debating")
        assert valid == False
        
        # Test vote validation
        valid, error = validate_vote("in")
        assert valid == True
        
        valid, error = validate_vote("maybe")
        assert valid == False
        
        # Test role validation
        valid, error = validate_role("proposition")
        assert valid == True
        
        valid, error = validate_role("neutral")
        assert valid == False
        
        console.print("  ✓ Validators working correctly")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_workflow_integration():
    """Test that state works in workflow-like scenarios"""
    console.print("\n[yellow]Test 11: Workflow Integration Pattern[/yellow]")
    
    try:
        # Simulate Agno workflow session_state usage
        
        # Step 1: Initialize (like workflow start)
        session_state = initialize_state(
            topic="UBI should be implemented",
            duration=300,
            exchanges_per_round=2,
            all_proposition_ids=["prop_analytical", "prop_emotional", "prop_rhetorical"],
            opposition_id="opp_pragmatist",
            active_proposition_id="prop_analytical"
        )
        
        # Step 2: Start debate (like debate step)
        session_state = set_phase(session_state, "debating")
        
        # Step 3: Exchange messages
        session_state = add_message(
            session_state, 
            "prop_analytical", "Analytical Debater", "proposition",
            "UBI would eliminate poverty based on data from multiple studies."
        )
        session_state = add_message(
            session_state,
            "opp_pragmatist", "Pragmatic Opposition", "opposition",
            "The cost would be prohibitive at $3 trillion annually."
        )
        
        # Step 4: Check if voting should trigger
        should_vote = should_trigger_voting(session_state)
        assert should_vote == True  # 2 exchanges = exchanges_per_round
        
        # Step 5: Voting round
        session_state = start_voting_round(session_state, "prop_analytical")
        session_state = add_vote(session_state, "prop_emotional", "Emotional", "in", "Good")
        session_state = add_vote(session_state, "prop_rhetorical", "Rhetorical", "out", "Weak")
        
        session_state, decision = complete_voting_round(session_state)
        
        # Step 6: Get summary
        stats = get_statistics(session_state)
        
        console.print("  ✓ Workflow integration pattern works")
        console.print(f"    Simulated {stats['total_messages']} exchanges")
        console.print(f"    Vote decision: {decision}")
        console.print(f"    Now in round: {session_state['current_round']}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def run_all_tests():
    """Run all state tests"""
    console.print("[bold magenta]╔═══════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║  CHECKPOINT 4: STATE MANAGEMENT TESTS     ║[/bold magenta]")
    console.print("[bold magenta]╚═══════════════════════════════════════════╝[/bold magenta]")
    
    tests = [
        ("Message Model", test_message_model),
        ("Vote Model", test_vote_model),
        ("DebateState Model", test_debate_state_model),
        ("Initialize State", test_initialize_state),
        ("Add Messages", test_add_messages),
        ("Voting Flow", test_voting_flow),
        ("Agent Switch", test_agent_switch),
        ("Get Recent History", test_get_recent_history),
        ("Statistics", test_statistics),
        ("Validators", test_validators),
        ("Workflow Integration", test_workflow_integration),
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    # Summary table
    console.print("\n[bold]═══ RESULTS ═══[/bold]\n")
    
    table = Table(title="Test Results", show_header=True)
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    
    passed = 0
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        style = "green" if result else "red"
        table.add_row(name, f"[{style}]{status}[/{style}]")
        if result:
            passed += 1
    
    console.print(table)
    
    total = len(tests)
    console.print(f"\n[bold]Passed: {passed}/{total}[/bold]")
    
    if passed == total:
        console.print("[bold green]✓ All tests passed! Checkpoint 4 complete.[/bold green]")
        return True
    else:
        console.print(f"[bold red]✗ {total - passed} test(s) failed[/bold red]")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

