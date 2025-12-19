#!/usr/bin/env python3
"""
Test Event Streaming

Tests the Agno custom events and SSE streaming functionality.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from streaming import (
    DebateEventType,
    DebateStartedEvent,
    AgentMessageCompleteEvent,
    VotingCompleteEvent,
    AgentSwitchEvent,
    DebateCompleteEvent,
    event_to_sse,
    SSEHandler,
    EventBuffer,
)

console = Console()


def test_custom_events():
    """Test creating custom Agno events"""
    console.print("\n[yellow]Test 1: Custom Event Creation[/yellow]")
    
    try:
        # Create debate started event
        event = DebateStartedEvent(
            topic="Universal Basic Income",
            duration=300,
            exchanges_per_round=3,
            first_debater_name="Analytical Debater",
            total_agents=7
        )
        
        assert event.event_type == "debate_started"
        assert event.topic == "Universal Basic Income"
        assert event.duration == 300
        
        # Create message event
        msg_event = AgentMessageCompleteEvent(
            agent_id="prop_1",
            agent_name="Analytical Debater",
            role="proposition",
            content="UBI would eliminate poverty.",
            word_count=5,
            round_number=1
        )
        
        assert msg_event.event_type == "agent_message_complete"
        assert msg_event.role == "proposition"
        
        console.print("  ✓ Custom events created successfully")
        console.print(f"    DebateStartedEvent type: {event.event_type}")
        console.print(f"    AgentMessageCompleteEvent type: {msg_event.event_type}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_event_to_sse():
    """Test converting events to SSE format"""
    console.print("\n[yellow]Test 2: Event to SSE Conversion[/yellow]")
    
    try:
        event = DebateStartedEvent(
            topic="Test Topic",
            duration=60,
            total_agents=5
        )
        
        sse = event_to_sse(event)
        
        assert "event: debate_started" in sse
        assert "data:" in sse
        assert "Test Topic" in sse
        
        console.print("  ✓ SSE conversion successful")
        console.print(f"    SSE format preview:")
        console.print(Panel(sse[:200] + "...", title="SSE Message", border_style="dim"))
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_sse_handler():
    """Test SSE handler"""
    console.print("\n[yellow]Test 3: SSE Handler[/yellow]")
    
    try:
        handler = SSEHandler()
        
        # Test format_event
        sse = handler.format_event("test_event", {"key": "value"})
        assert "event: test_event" in sse
        assert "data:" in sse
        
        # Test heartbeat
        heartbeat = handler.heartbeat()
        assert ": heartbeat" in heartbeat
        
        console.print("  ✓ SSE handler works correctly")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_event_buffer():
    """Test event buffering"""
    console.print("\n[yellow]Test 4: Event Buffer[/yellow]")
    
    try:
        buffer = EventBuffer(max_size=10)
        
        # Add events
        for i in range(5):
            buffer.add({"id": i, "message": f"Event {i}"})
        
        assert len(buffer) == 5
        
        events = buffer.get_all()
        assert len(events) == 5
        
        # Test overflow
        for i in range(10):
            buffer.add({"id": i + 100})
        
        assert len(buffer) == 10  # Max size enforced
        
        # Test clear
        buffer.clear()
        assert len(buffer) == 0
        
        console.print("  ✓ Event buffer works correctly")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_event_types():
    """Test all event types are defined"""
    console.print("\n[yellow]Test 5: Event Types Enum[/yellow]")
    
    try:
        expected_types = [
            "debate_started",
            "debate_complete",
            "agent_message_chunk",
            "agent_message_complete",
            "voting_initiated",
            "vote_cast",
            "voting_complete",
            "agent_switch",
            "timer_update",
            "error",
        ]
        
        for event_type in expected_types:
            # Verify enum has this value
            found = any(e.value == event_type for e in DebateEventType)
            assert found, f"Missing event type: {event_type}"
        
        console.print("  ✓ All event types defined")
        console.print(f"    Total event types: {len(list(DebateEventType))}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def test_full_event_flow():
    """Test a simulated event flow"""
    console.print("\n[yellow]Test 6: Simulated Event Flow[/yellow]")
    
    try:
        handler = SSEHandler()
        buffer = EventBuffer()
        
        # Simulate debate events
        events = [
            DebateStartedEvent(topic="Test", duration=60),
            AgentMessageCompleteEvent(
                agent_name="Agent 1",
                role="proposition",
                content="Opening argument",
                round_number=1
            ),
            AgentMessageCompleteEvent(
                agent_name="Opposition",
                role="opposition",
                content="Counter argument",
                round_number=1
            ),
            VotingCompleteEvent(
                evaluating_agent_name="Agent 1",
                in_votes=3,
                out_votes=1,
                decision="stay"
            ),
            DebateCompleteEvent(
                topic="Test",
                total_messages=2,
                total_rounds=1
            ),
        ]
        
        sse_messages = []
        for event in events:
            sse = event_to_sse(event)
            sse_messages.append(sse)
            buffer.add(event)
        
        assert len(sse_messages) == 5
        assert len(buffer) == 5
        
        console.print("  ✓ Event flow simulation successful")
        console.print(f"    Events processed: {len(events)}")
        console.print(f"    SSE messages generated: {len(sse_messages)}")
        return True
    except Exception as e:
        console.print(f"  ✗ Failed: {e}")
        return False


def run_all_tests():
    """Run all streaming tests"""
    console.print("[bold magenta]╔═══════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║     EVENT STREAMING TESTS                 ║[/bold magenta]")
    console.print("[bold magenta]╚═══════════════════════════════════════════╝[/bold magenta]")
    
    tests = [
        ("Custom Event Creation", test_custom_events),
        ("Event to SSE Conversion", test_event_to_sse),
        ("SSE Handler", test_sse_handler),
        ("Event Buffer", test_event_buffer),
        ("Event Types Enum", test_event_types),
        ("Simulated Event Flow", test_full_event_flow),
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
        console.print("[bold green]✓ All streaming tests passed![/bold green]")
        return True
    else:
        console.print(f"[bold red]✗ {total - passed} test(s) failed[/bold red]")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

