#!/usr/bin/env python3
"""
Test dynamically created agents
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import (
    get_all_proposition_agents,
    get_opposition_agent,
    get_moderator_agent,
    get_agent_info
)
from rich.console import Console

console = Console()


def test_agent_creation():
    """Test creating agents from config"""
    console.print("[bold blue]Testing Dynamic Agent Creation[/bold blue]\n")
    
    # Get agent info
    info = get_agent_info()
    console.print(f"Total agents configured: {info['total_agents']}")
    
    # Create all agents
    console.print("\n[yellow]Creating proposition agents...[/yellow]")
    prop_agents = get_all_proposition_agents()
    console.print(f"✓ Created {len(prop_agents)} proposition agents")
    
    for agent in prop_agents:
        console.print(f"  - {agent.name} ({agent.personality_type})")
    
    console.print("\n[yellow]Creating opposition agent...[/yellow]")
    opp_agent = get_opposition_agent()
    console.print(f"✓ Created: {opp_agent.name} ({opp_agent.personality_type})")
    
    console.print("\n[yellow]Creating moderator agent...[/yellow]")
    mod_agent = get_moderator_agent()
    console.print(f"✓ Created: {mod_agent.name} ({mod_agent.personality_type})")
    
    return prop_agents, opp_agent, mod_agent


def test_agent_responses():
    """Test that each agent responds with their personality"""
    console.print("\n[bold blue]Testing Agent Personalities[/bold blue]\n")
    
    prop_agents, opp_agent, mod_agent = test_agent_creation()
    
    test_prompt = "Make a brief opening statement about why communism is not healthy for the economy."
    
    console.print(f"\n[cyan]Test Prompt:[/cyan] {test_prompt}\n")
    
    # Test first proposition agent
    console.print(f"[green]Testing {prop_agents[0].name}:[/green]")
    console.print("(To make actual LLM calls, set OPENAI_API_KEY in .env and uncomment the agent.print_response line)\n")
    
    # Uncomment to test actual LLM response:
    # prop_agents[0].print_response(test_prompt, stream=True)
    
    console.print("[green]✓ Agent creation and configuration successful![/green]")


if __name__ == "__main__":
    test_agent_responses()

