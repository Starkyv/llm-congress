#!/usr/bin/env python3
"""
Run Debate Workflow

Simple script to run the Agno debate workflow.

Usage:
    python run_debate.py "Should AI be regulated?"
    python run_debate.py --topic "UBI should be implemented" --duration 120
    python run_debate.py --topic "Climate action" --rounds 3
"""

import sys
import os
import argparse

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from workflows.debate_workflow import (
    create_agno_workflow,
    create_debate_loop_workflow,
    DebateWorkflow,
)


def run_agno_workflow(topic: str, duration: int = 300, exchanges: int = 3):
    """
    Run the basic Agno workflow (single cycle).
    
    This uses Agno's built-in workflow execution.
    """
    print(f"\n{'='*60}")
    print(f"🎤 AGNO DEBATE WORKFLOW")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Duration: {duration}s | Exchanges per round: {exchanges}")
    print(f"{'='*60}\n")
    
    # Create workflow
    workflow = create_agno_workflow(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges
    )
    
    # Run with streaming output
    # The input kicks off the workflow
    workflow.print_response(
        input=f"Begin debate on: {topic}",
        stream=True
    )
    
    # Get final state (session_state is updated in-place during workflow)
    final_state = workflow.session_state
    
    print(f"\n{'='*60}")
    print("📊 FINAL STATE")
    print(f"{'='*60}")
    print(f"Topic: {final_state.get('topic', 'Unknown')}")
    print(f"Messages: {len(final_state.get('messages', []))}")
    print(f"Switches: {len(final_state.get('agent_switches', []))}")
    print(f"Phase: {final_state.get('phase', 'unknown')}")
    print(f"Status: {final_state.get('status', 'unknown')}")
    if final_state.get('summary'):
        print(f"Summary: {final_state.get('summary', '')[:100]}...")
    print(f"{'='*60}\n")
    
    return final_state


def run_multi_round_workflow(topic: str, duration: int = 300, exchanges: int = 3, rounds: int = 3):
    """
    Run the multi-round debate workflow.
    
    This runs multiple debate cycles before concluding.
    """
    print(f"\n{'='*60}")
    print(f"🎤 MULTI-ROUND DEBATE WORKFLOW")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Duration: {duration}s | Exchanges: {exchanges} | Rounds: {rounds}")
    print(f"{'='*60}\n")
    
    # Create workflow with multiple rounds
    workflow = create_debate_loop_workflow(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges,
        max_rounds=rounds
    )
    
    # Run with streaming
    workflow.print_response(
        input=f"Begin {rounds}-round debate on: {topic}",
        stream=True
    )
    
    return workflow.session_state


def run_custom_workflow(topic: str, duration: int = 300, exchanges: int = 3):
    """
    Run the custom DebateWorkflow class (non-Agno, generator-based).
    
    This uses the original custom implementation with event streaming.
    """
    print(f"\n{'='*60}")
    print(f"🎤 CUSTOM DEBATE WORKFLOW (Event Streaming)")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Duration: {duration}s | Exchanges: {exchanges}")
    print(f"{'='*60}\n")
    
    # Create and run custom workflow
    workflow = DebateWorkflow()
    
    # Stream events
    for event in workflow.run(
        topic=topic,
        duration=duration,
        exchanges_per_round=exchanges,
        stream=True
    ):
        # Print each event
        event_type = event.event_type.value
        data = event.data
        
        if event_type == "agent_message_complete":
            agent = data.get("agent_name", "Unknown")
            role = data.get("role", "")
            content = data.get("content", "")[:200]
            print(f"\n[{role.upper()}] {agent}:")
            print(f"  {content}...")
        
        elif event_type == "voting_complete":
            tally = data.get("vote_tally", {})
            decision = data.get("decision", "")
            print(f"\n📊 VOTE: In={tally.get('in', 0)} Out={tally.get('out', 0)} → {decision}")
        
        elif event_type == "agent_switch":
            old = data.get("old_agent_name", "")
            new = data.get("new_agent_name", "")
            print(f"\n🔄 SWITCH: {old} → {new}")
        
        elif event_type == "debate_complete":
            print(f"\n✅ Debate complete!")
    
    return workflow.get_state()


def main():
    parser = argparse.ArgumentParser(description="Run a debate workflow")
    parser.add_argument("topic", nargs="?", default="Universal Basic Income should be implemented",
                       help="The debate topic")
    parser.add_argument("--duration", "-d", type=int, default=300,
                       help="Debate duration in seconds (default: 300)")
    parser.add_argument("--exchanges", "-e", type=int, default=3,
                       help="Exchanges before voting (default: 3)")
    parser.add_argument("--rounds", "-r", type=int, default=None,
                       help="Number of debate rounds (enables multi-round mode)")
    parser.add_argument("--mode", "-m", choices=["agno", "multi", "custom"], default="agno",
                       help="Workflow mode: agno (default), multi (multi-round), custom (event streaming)")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "multi" or args.rounds:
            rounds = args.rounds or 3
            run_multi_round_workflow(args.topic, args.duration, args.exchanges, rounds)
        elif args.mode == "custom":
            run_custom_workflow(args.topic, args.duration, args.exchanges)
        else:
            run_agno_workflow(args.topic, args.duration, args.exchanges)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Debate interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()

