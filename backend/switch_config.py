#!/usr/bin/env python3
"""
Utility to switch between different agent configurations
"""
import shutil
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.prompt import Prompt

console = Console()


def list_available_configs():
    """List all available configuration files"""
    config_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "config"
    configs = list(config_dir.glob("agent_config*.json"))
    
    return [c.name for c in configs if c.name != "agent_config.json"]


def switch_configuration():
    """Interactive configuration switcher"""
    console.print("[bold]Available Configurations:[/bold]\n")
    
    configs = list_available_configs()
    
    if not configs:
        console.print("[red]No alternative configurations found in config/ directory[/red]")
        return
    
    for idx, config_name in enumerate(configs, 1):
        console.print(f"{idx}. {config_name}")
    
    console.print(f"{len(configs) + 1}. Cancel")
    
    choice = Prompt.ask(
        "\nSelect configuration",
        choices=[str(i) for i in range(1, len(configs) + 2)],
        default=str(len(configs) + 1)
    )
    
    choice_idx = int(choice) - 1
    
    if choice_idx == len(configs):
        console.print("Cancelled")
        return
    
    selected_config = configs[choice_idx]
    
    config_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "config"
    
    # Backup current config
    current_config = config_dir / "agent_config.json"
    if current_config.exists():
        backup_path = config_dir / "agent_config.backup.json"
        shutil.copy(current_config, backup_path)
        console.print(f"[yellow]Backed up current config to {backup_path}[/yellow]")
    
    # Copy selected config
    source = config_dir / selected_config
    shutil.copy(source, current_config)
    
    console.print(f"[green]✓ Switched to {selected_config}[/green]")
    console.print("\nRun 'python validate_config.py' to verify the new configuration")


if __name__ == "__main__":
    switch_configuration()

