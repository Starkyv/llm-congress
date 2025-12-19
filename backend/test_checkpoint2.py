#!/usr/bin/env python3
"""
Comprehensive test for Checkpoint 2 - Dynamic Agent Creation
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console

console = Console()


def run_checkpoint2_tests():
    """Run all tests for checkpoint 2"""
    
    console.print("[bold blue]CHECKPOINT 2 VALIDATION[/bold blue]\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Config loads
    console.print("[yellow]Test 1: Configuration Loading[/yellow]")
    tests_total += 1
    try:
        from config import config
        console.print("  ✓ Config loaded successfully")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Config loading failed: {e}")
    
    # Test 2: Config validation
    console.print("\n[yellow]Test 2: Configuration Validation[/yellow]")
    tests_total += 1
    try:
        from config import AgentConfig
        cfg = AgentConfig()
        console.print("  ✓ Config structure is valid")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Config validation failed: {e}")
    
    # Test 3: Agent factory creation
    console.print("\n[yellow]Test 3: Agent Factory[/yellow]")
    tests_total += 1
    try:
        from agents.agent_factory import AgentFactory
        factory = AgentFactory()
        console.print("  ✓ Agent factory created")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Agent factory creation failed: {e}")
    
    # Test 4: Proposition agents creation
    console.print("\n[yellow]Test 4: Proposition Agents Creation[/yellow]")
    tests_total += 1
    try:
        from agents import get_all_proposition_agents
        prop_agents = get_all_proposition_agents()
        console.print(f"  ✓ Created {len(prop_agents)} proposition agents")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Proposition agents creation failed: {e}")
    
    # Test 5: Opposition agent creation
    console.print("\n[yellow]Test 5: Opposition Agent Creation[/yellow]")
    tests_total += 1
    try:
        from agents import get_opposition_agent
        opp = get_opposition_agent()
        console.print(f"  ✓ Created opposition agent: {opp.name}")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Opposition agent creation failed: {e}")
    
    # Test 6: Moderator agent creation
    console.print("\n[yellow]Test 6: Moderator Agent Creation[/yellow]")
    tests_total += 1
    try:
        from agents import get_moderator_agent
        mod = get_moderator_agent()
        console.print(f"  ✓ Created moderator agent: {mod.name}")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Moderator agent creation failed: {e}")
    
    # Test 7: Random selection
    console.print("\n[yellow]Test 7: Random Agent Selection[/yellow]")
    tests_total += 1
    try:
        from agents import select_random_proposition
        random_agent = select_random_proposition()
        console.print(f"  ✓ Selected random agent: {random_agent.name}")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Random selection failed: {e}")
    
    # Test 8: Agent info retrieval
    console.print("\n[yellow]Test 8: Agent Information Retrieval[/yellow]")
    tests_total += 1
    try:
        from agents import get_agent_info
        info = get_agent_info()
        console.print(f"  ✓ Retrieved info for {info['total_agents']} total agents")
        tests_passed += 1
    except Exception as e:
        console.print(f"  ✗ Info retrieval failed: {e}")
    
    # Results
    console.print(f"\n[bold]Results: {tests_passed}/{tests_total} tests passed[/bold]")
    
    if tests_passed == tests_total:
        console.print("[green]✓ All tests passed! Checkpoint 2 complete.[/green]")
        return True
    else:
        console.print(f"[red]✗ {tests_total - tests_passed} test(s) failed[/red]")
        return False


if __name__ == "__main__":
    success = run_checkpoint2_tests()
    sys.exit(0 if success else 1)

