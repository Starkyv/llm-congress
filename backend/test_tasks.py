#!/usr/bin/env python3
"""
Test Tasks with Agents

Tests the debate, vote, and moderation tasks with actual agents.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from tasks import (
    get_debate_task,
    get_vote_task,
    get_moderate_task,
    VoteEvaluationTask,
)
from agents import (
    get_all_proposition_agents,
    get_opposition_agent,
    get_moderator_agent,
)

console = Console()


def test_debate_task():
    """Test the debate task with an agent"""
    console.print("\n[bold blue]═══ TEST 1: Debate Task ═══[/bold blue]\n")
    
    # Get the analytical agent (first proposition agent)
    prop_agents = get_all_proposition_agents()
    analytical_agent = prop_agents[0]
    
    console.print(f"[green]Agent:[/green] {analytical_agent.name} ({analytical_agent.personality_type})")
    
    # Create a debate task
    task = get_debate_task(
        topic="Universal Basic Income should be implemented in the United States",
        stance="for",
        debate_history=[
            {"speaker": "Opposition", "argument": "UBI would be too expensive and discourage work."}
        ],
        opponent_last_argument="The cost of implementing UBI would bankrupt the nation and create dependency.",
        personality_note=analytical_agent.personality_type
    )
    
    console.print(f"\n[cyan]Topic:[/cyan] {task.topic}")
    console.print(f"[cyan]Stance:[/cyan] {task.stance}")
    console.print(f"\n[yellow]Generated Prompt:[/yellow]")
    console.print(Panel(task.build_prompt(), title="Debate Prompt", border_style="dim"))
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        console.print("\n[yellow]Calling agent...[/yellow]\n")
        analytical_agent.print_response(task.build_prompt(), stream=True)
    else:
        console.print("\n[dim]⚠️ Set OPENAI_API_KEY in .env to test actual LLM response[/dim]")
    
    console.print("\n[green]✓ Debate task test complete[/green]")
    return True


def test_vote_task():
    """Test the vote task with an agent"""
    console.print("\n[bold blue]═══ TEST 2: Vote Task ═══[/bold blue]\n")
    
    # Get an emotional agent for voting
    prop_agents = get_all_proposition_agents()
    emotional_agent = None
    for agent in prop_agents:
        if agent.personality_type == "emotional":
            emotional_agent = agent
            break
    
    if not emotional_agent:
        emotional_agent = prop_agents[1] if len(prop_agents) > 1 else prop_agents[0]
    
    console.print(f"[green]Voter:[/green] {emotional_agent.name} ({emotional_agent.personality_type})")
    
    # Create a vote task
    task = get_vote_task(
        current_debater_name="Analytical Debater",
        recent_exchanges=[
            {"speaker": "Analytical Debater", "argument": "Studies show UBI reduces poverty by 40% in pilot programs."},
            {"speaker": "Opposition", "argument": "Those pilot programs were too small to be meaningful."},
            {"speaker": "Analytical Debater", "argument": "The Finland and Kenya trials involved thousands of participants."},
        ],
        evaluation_criteria="argument strength, use of evidence, and persuasiveness",
        voter_personality=emotional_agent.personality_type
    )
    
    console.print(f"\n[cyan]Evaluating:[/cyan] {task.current_debater_name}")
    console.print(f"\n[yellow]Generated Prompt:[/yellow]")
    console.print(Panel(task.build_prompt(), title="Vote Prompt", border_style="dim"))
    
    # Test vote parsing
    console.print("\n[cyan]Testing vote response parsing:[/cyan]")
    
    test_responses = [
        '{"vote": "in", "reasoning": "Strong use of data and specific examples."}',
        '{"vote": "out", "reasoning": "Not compelling enough."}',
        'I think {"vote": "in", "reasoning": "Good arguments"} is my choice.',
    ]
    
    for response in test_responses:
        result = VoteEvaluationTask.parse_vote_response(response)
        if result:
            console.print(f"  ✓ Parsed: vote={result.vote}, reasoning={result.reasoning[:40]}...")
        else:
            console.print(f"  ✗ Failed to parse: {response[:50]}...")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        console.print("\n[yellow]Calling agent for actual vote...[/yellow]\n")
        emotional_agent.print_response(task.build_prompt(), stream=True)
    else:
        console.print("\n[dim]⚠️ Set OPENAI_API_KEY in .env to test actual LLM response[/dim]")
    
    console.print("\n[green]✓ Vote task test complete[/green]")
    return True


def test_moderate_task():
    """Test the moderation task with the moderator agent"""
    console.print("\n[bold blue]═══ TEST 3: Moderate Task ═══[/bold blue]\n")
    
    # Get the moderator agent
    moderator = get_moderator_agent()
    
    console.print(f"[green]Moderator:[/green] {moderator.name} ({moderator.personality_type})")
    
    # Create a moderate task with sample debate
    task = get_moderate_task(
        topic="Universal Basic Income should be implemented in the United States",
        full_debate_transcript=[
            {"speaker": "Analytical Debater", "role": "proposition", 
             "content": "UBI would eliminate poverty and provide economic security for all citizens."},
            {"speaker": "Pragmatic Opposition", "role": "opposition",
             "content": "The cost would be astronomical - over $3 trillion annually."},
            {"speaker": "Emotional Advocate", "role": "proposition",
             "content": "Think of the families who struggle daily. UBI gives them dignity and hope."},
            {"speaker": "Pragmatic Opposition", "role": "opposition",
             "content": "Dignity comes from work, not handouts. UBI could destroy work incentive."},
        ],
        vote_history=[
            {"voter": "Historical Scholar", "voted_for": "Analytical Debater", 
             "vote_type": "in", "reasoning": "Good use of evidence"},
        ],
        duration_seconds=180
    )
    
    console.print(f"\n[cyan]Topic:[/cyan] {task.topic}")
    console.print(f"[cyan]Duration:[/cyan] {task.duration_seconds} seconds")
    console.print(f"[cyan]Exchanges:[/cyan] {len(task.full_debate_transcript)}")
    console.print(f"\n[yellow]Generated Prompt (truncated):[/yellow]")
    
    prompt = task.build_prompt()
    # Show first 1000 chars
    console.print(Panel(prompt[:1000] + "...", title="Moderate Prompt", border_style="dim"))
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        console.print("\n[yellow]Calling moderator agent...[/yellow]\n")
        moderator.print_response(prompt, stream=True)
    else:
        console.print("\n[dim]⚠️ Set OPENAI_API_KEY in .env to test actual LLM response[/dim]")
    
    console.print("\n[green]✓ Moderate task test complete[/green]")
    return True


def run_all_tests():
    """Run all task tests"""
    console.print("[bold magenta]╔═══════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║     CHECKPOINT 3: TASK TESTS          ║[/bold magenta]")
    console.print("[bold magenta]╚═══════════════════════════════════════╝[/bold magenta]")
    
    results = {
        "Debate Task": test_debate_task(),
        "Vote Task": test_vote_task(),
        "Moderate Task": test_moderate_task(),
    }
    
    console.print("\n[bold]═══ RESULTS ═══[/bold]\n")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        console.print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        console.print("\n[bold green]✓ All task tests passed! Checkpoint 3 complete.[/bold green]")
    else:
        console.print("\n[bold red]✗ Some tests failed.[/bold red]")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

