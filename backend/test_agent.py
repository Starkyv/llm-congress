#!/usr/bin/env python3
"""
Test individual agents from configuration
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from agents import get_all_proposition_agents, get_opposition_agent, get_agent_info
from rich.console import Console
from rich.prompt import Prompt

console = Console()


def test_single_agent():
    """Test a single agent interactively"""
    
    # Get agent info
    info = get_agent_info()
    
    console.print("[bold]Available Agents:[/bold]\n")
    
    # List proposition agents
    prop_agents = get_all_proposition_agents()
    for idx, agent in enumerate(prop_agents, 1):
        console.print(f"{idx}. {agent.name} ({agent.personality_type})")
    
    # Add opposition
    opp_agent = get_opposition_agent()
    console.print(f"{len(prop_agents) + 1}. {opp_agent.name} ({opp_agent.personality_type})")
    
    # Get choice
    choice = Prompt.ask(
        "\nSelect agent to test",
        choices=[str(i) for i in range(1, len(prop_agents) + 2)],
        default="1"
    )
    
    choice_idx = int(choice) - 1
    
    if choice_idx < len(prop_agents):
        selected_agent = prop_agents[choice_idx]
    else:
        selected_agent = opp_agent
    
    console.print(f"\n[green]Testing: {selected_agent.name}[/green]")
    console.print(f"Personality: {selected_agent.personality_type}\n")
    
    # Get test prompt
    test_topic = Prompt.ask(
        "Enter debate topic",
        default="Communism is not healthy for the economy"
    )
    
    console.print(f"\n[cyan]Prompt:[/cyan] Argue about: {test_topic}\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        console.print("[yellow]⚠️  OPENAI_API_KEY not set. Set it in backend/.env to make actual LLM calls.[/yellow]")
        console.print("[dim]Skipping actual LLM call...[/dim]")
        return
    
    # Call agent
    console.print("[yellow]Calling agent...[/yellow]\n")
    selected_agent.print_response(
        f"Make a brief opening argument about: {test_topic}",
        stream=True
    )


if __name__ == "__main__":
    test_single_agent()
