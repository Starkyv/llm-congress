#!/usr/bin/env python3
"""
Comprehensive tests for Checkpoint 5 - Debate Workflow

Tests the complete debate workflow including initialization,
debate turns, voting, agent switching, and conclusion.
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from workflows import (
    DebateWorkflow,
    create_debate_workflow,
    DebateEvent,
    DebateEventType,
    initialize_debate,
)
from workflows.steps.debate_turn import check_round_completion
from state import add_message, set_phase
from agents import get_all_proposition_agents, get_opposition_agent

console = Console()


def test_workflow_initialization():
    """Test workflow initialization step"""
    console.print("\n[yellow]Test 1: Workflow Initialization[/yellow]")
    
    try:
        state, start_event = initialize_debate(
            topic="Universal Basic Income should be implemented",
            duration=120,
            exchanges_per_round=2
        )
        
        assert state is not None
        assert state["topic"] == "Universal Basic Income should be implemented"
        assert state["duration"] == 120
        assert state["exchanges_per_round"] == 2
        assert state["phase"] == "debating"
        assert len(state.get("all_proposition_ids", [])) > 0
        assert state.get("active_proposition_id") is not None
        
        assert start_event.event_type == DebateEventType.DEBATE_STARTED
        assert "first_debater" in start_event.data
        
        console.print("  ✓ Initialization successful")
        console.print(f"    Topic: {state['topic']}")
        console.print(f"    First debater: {start_event.data['first_debater']}")
        console.print(f"    Observers: {len(start_event.data['observers'])}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_round_completion_check():
    """Test round completion checking"""
    console.print("\n[yellow]Test 2: Round Completion Check[/yellow]")
    
    try:
        state, _ = initialize_debate(
            topic="Test topic",
            duration=300,
            exchanges_per_round=2
        )
        
        # Initially should continue
        result = check_round_completion(state)
        assert result == "continue", f"Expected 'continue', got '{result}'"
        
        # Add messages to reach threshold
        state = add_message(state, "agent1", "Agent 1", "proposition", "Argument 1")
        result = check_round_completion(state)
        assert result == "continue"
        
        state = add_message(state, "agent2", "Agent 2", "opposition", "Counter 1")
        result = check_round_completion(state)
        assert result == "vote", f"Expected 'vote' after 2 exchanges, got '{result}'"
        
        console.print("  ✓ Round completion check works correctly")
        console.print(f"    After 0 exchanges: continue")
        console.print(f"    After 2 exchanges: vote")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_workflow_creation():
    """Test creating workflow instance"""
    console.print("\n[yellow]Test 3: Workflow Creation[/yellow]")
    
    try:
        workflow = create_debate_workflow()
        
        assert workflow is not None
        assert workflow.name == "Debate Simulation"
        assert workflow.is_running == False
        
        console.print("  ✓ Workflow created successfully")
        console.print(f"    Name: {workflow.name}")
        console.print(f"    Version: {workflow.version}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_event_types():
    """Test event type definitions"""
    console.print("\n[yellow]Test 4: Event Types[/yellow]")
    
    try:
        # Test all event types exist
        event_types = [
            DebateEventType.DEBATE_STARTED,
            DebateEventType.DEBATE_COMPLETE,
            DebateEventType.AGENT_MESSAGE_CHUNK,
            DebateEventType.AGENT_MESSAGE_COMPLETE,
            DebateEventType.VOTING_INITIATED,
            DebateEventType.VOTE_CAST,
            DebateEventType.VOTING_COMPLETE,
            DebateEventType.AGENT_SWITCH,
            DebateEventType.TIMER_UPDATE,
            DebateEventType.ERROR,
        ]
        
        for et in event_types:
            assert et.value is not None
        
        # Test event creation
        event = DebateEvent(
            event_type=DebateEventType.DEBATE_STARTED,
            data={"topic": "Test", "duration": 60},
            timestamp=datetime.now().isoformat()
        )
        
        assert event.event_type == DebateEventType.DEBATE_STARTED
        assert event.data["topic"] == "Test"
        
        # Test SSE format
        sse = event.to_sse_format()
        assert "event: debate_started" in sse
        assert "data:" in sse
        
        console.print("  ✓ Event types defined correctly")
        console.print(f"    Total event types: {len(event_types)}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_agent_loading():
    """Test that agents are loaded correctly for workflow"""
    console.print("\n[yellow]Test 5: Agent Loading[/yellow]")
    
    try:
        prop_agents = get_all_proposition_agents()
        opp_agent = get_opposition_agent()
        
        assert len(prop_agents) >= 1
        assert opp_agent is not None
        
        # Check agents have required attributes
        for agent in prop_agents:
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'personality_type')
        
        assert hasattr(opp_agent, 'agent_id')
        
        console.print("  ✓ Agents loaded correctly")
        console.print(f"    Proposition agents: {len(prop_agents)}")
        console.print(f"    Opposition agent: {opp_agent.name}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_short_workflow_run():
    """Test running a very short workflow (if API key available)"""
    console.print("\n[yellow]Test 6: Short Workflow Run[/yellow]")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        console.print("  ⚠ Skipped: OPENAI_API_KEY not set")
        console.print("    Set OPENAI_API_KEY in .env to test actual workflow")
        return True  # Not a failure, just skipped
    
    try:
        workflow = create_debate_workflow()
        
        events_received = []
        event_count = 0
        
        console.print("  Running short 30-second debate...")
        
        # Run with very short duration
        gen = workflow.run(
            topic="Shorter work weeks improve productivity",
            duration=30,  # Very short
            exchanges_per_round=1,  # Quick voting
            stream=False  # Don't stream chunks
        )
        
        final_state = None
        try:
            while True:
                event = next(gen)
                events_received.append(event.event_type)
                event_count += 1
                
                # Print major events
                if event.event_type in [
                    DebateEventType.DEBATE_STARTED,
                    DebateEventType.AGENT_MESSAGE_COMPLETE,
                    DebateEventType.VOTING_COMPLETE,
                    DebateEventType.DEBATE_COMPLETE,
                ]:
                    console.print(f"    Event: {event.event_type.value}")
        except StopIteration as e:
            final_state = e.value
        
        # Verify workflow completed
        assert DebateEventType.DEBATE_STARTED in events_received
        assert final_state is not None
        
        console.print(f"  ✓ Workflow completed")
        console.print(f"    Total events: {event_count}")
        console.print(f"    Final phase: {final_state.get('phase', 'unknown')}")
        return True
        
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_stop():
    """Test workflow stop functionality"""
    console.print("\n[yellow]Test 7: Workflow Stop[/yellow]")
    
    try:
        workflow = create_debate_workflow()
        
        # Test stop before running
        workflow.stop()
        assert workflow.is_running == False
        
        console.print("  ✓ Workflow stop works correctly")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_event_collection():
    """Test event collection during workflow"""
    console.print("\n[yellow]Test 8: Event Collection[/yellow]")
    
    try:
        workflow = create_debate_workflow()
        
        # Events should be empty initially
        assert len(workflow.get_events()) == 0
        
        # State should be empty initially
        assert len(workflow.get_state()) == 0
        
        console.print("  ✓ Event collection initialized correctly")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def run_all_tests():
    """Run all workflow tests"""
    console.print("[bold magenta]╔═══════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║     CHECKPOINT 5: WORKFLOW TESTS          ║[/bold magenta]")
    console.print("[bold magenta]╚═══════════════════════════════════════════╝[/bold magenta]")
    
    tests = [
        ("Workflow Initialization", test_workflow_initialization),
        ("Round Completion Check", test_round_completion_check),
        ("Workflow Creation", test_workflow_creation),
        ("Event Types", test_event_types),
        ("Agent Loading", test_agent_loading),
        ("Short Workflow Run", test_short_workflow_run),
        ("Workflow Stop", test_workflow_stop),
        ("Event Collection", test_event_collection),
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
        console.print("[bold green]✓ All tests passed! Checkpoint 5 complete.[/bold green]")
        return True
    else:
        console.print(f"[bold red]✗ {total - passed} test(s) failed[/bold red]")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

