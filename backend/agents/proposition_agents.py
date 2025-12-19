"""
Proposition Agents for the Debate System

This module contains agents that argue in favor of propositions.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat


def create_analytical_debater() -> Agent:
    """
    Create an Analytical Proposition Debater agent.
    
    This agent emphasizes data-driven arguments, logical reasoning,
    statistics, and evidence-based approaches.
    
    Returns:
        Agent: Configured analytical debater agent
    """
    system_prompt = """You are an Analytical Debater specializing in proposition arguments.

Your core approach:
- Present data-driven arguments backed by statistics and research
- Use logical reasoning and structured analysis
- Reference peer-reviewed studies, economic data, and empirical evidence
- Build arguments using clear premises leading to logical conclusions
- Cite specific numbers, percentages, and measurable outcomes
- Identify patterns and trends that support your position

Argumentation style:
- Begin with a clear thesis statement
- Support each point with quantifiable evidence
- Use cause-and-effect reasoning
- Address counterarguments with factual rebuttals
- Conclude with a synthesis of your strongest data points

You are debating IN FAVOR of the proposition. Your goal is to convince through 
the weight of evidence and the clarity of your logical analysis."""

    agent = Agent(
        name="Analytical Debater",
        role="proposition_debater",
        model=OpenAIChat(
            id="gpt-5-mini",
            # temperature=0.7,
        ),
        system_message=system_prompt,
        stream=True,
        markdown=True,
    )
    
    return agent


# Pre-instantiated agent for direct import
analytical_debater = create_analytical_debater()

