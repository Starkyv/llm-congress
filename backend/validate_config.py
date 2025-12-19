#!/usr/bin/env python3
"""
Validate agent configuration file
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AgentConfig
from agents import get_agent_info
from rich.console import Console
from rich.table import Table

console = Console()


def validate_configuration():
    """Validate and display agent configuration"""
    try:
        # Load config
        config = AgentConfig()
        console.print("[green]✓ Configuration file loaded successfully[/green]")
        
        # Get agent info
        info = get_agent_info()
        
        # Display summary
        console.print(f"\n[bold]Total Agents:[/bold] {info['total_agents']}")
        console.print(f"[bold]Proposition Agents:[/bold] {info['proposition_count']}")
        
        # Create table for proposition agents
        prop_table = Table(title="Proposition Agents", show_header=True)
        prop_table.add_column("ID", style="cyan")
        prop_table.add_column("Name", style="green")
        prop_table.add_column("Personality", style="yellow")
        
        for agent in info['proposition_agents']:
            prop_table.add_row(agent['id'], agent['name'], agent['personality'])
        
        console.print(prop_table)
        
        # Display opposition
        console.print(f"\n[bold]Opposition Agent:[/bold]")
        console.print(f"  ID: {info['opposition']['id']}")
        console.print(f"  Name: {info['opposition']['name']}")
        console.print(f"  Personality: {info['opposition']['personality']}")
        
        # Display moderator
        console.print(f"\n[bold]Moderator Agent:[/bold]")
        console.print(f"  ID: {info['moderator']['id']}")
        console.print(f"  Name: {info['moderator']['name']}")
        console.print(f"  Personality: {info['moderator']['personality']}")
        
        console.print("\n[green]✓ Configuration is valid![/green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]✗ Configuration validation failed:[/red]")
        console.print(f"[red]{str(e)}[/red]")
        return False


if __name__ == "__main__":
    success = validate_configuration()
    sys.exit(0 if success else 1)

