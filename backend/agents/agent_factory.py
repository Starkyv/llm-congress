"""
Agent Factory for Dynamic Agent Creation

This module creates agents dynamically from configuration.
"""

from typing import List, Optional
import random
import sys
import os
from agno.models.openrouter import OpenRouter

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from agno.agent import Agent
from agno.models.openai import OpenAIChat


class AgentFactory:
    """Factory for creating agents dynamically from configuration"""
    
    def __init__(self):
        self.debate_config = config.get_debate_config()
        self.proposition_configs = config.get_proposition_agents_config()
        self.opposition_config = config.get_opposition_agent_config()
        self.moderator_config = config.get_moderator_agent_config()
        
        # Cache created agents
        self._proposition_agents = None
        self._opposition_agent = None
        self._moderator_agent = None
    
    def _create_agent_from_config(self, agent_config: dict, role: str) -> Agent:
        """Create a single agent from configuration"""
        # Get temperature - use agent-specific or fall back to debate config
        temperature = agent_config.get('temperature', self.debate_config.get('temperature', 0.7))
        
        # Get model - use agent-specific or fall back to debate config
        model_id = agent_config.get('model', self.debate_config.get('model', 'gpt-4o-mini'))
        
        # Build system prompt
        system_prompt = self._build_system_prompt(agent_config, role)
        
        # Create agent using Agno with OpenRouter
        agent = Agent(
            name=agent_config['name'],
            role=role,
            model=OpenRouter(
                id=model_id,
                # temperature=temperature,
                max_completion_tokens=self.debate_config.get('max_tokens', 1000),
            ),
            instructions=[system_prompt],
            markdown=True,
            reasoning=False
            # stream=True,
        )
        
        # Add metadata as attributes
        agent.agent_id = agent_config['id']
        agent.personality_type = agent_config['personality_type']
        agent.role_type = role
        
        return agent
    
    def _build_system_prompt(self, agent_config: dict, role: str) -> str:
        """Build comprehensive system prompt for agent"""
        base_prompt = f"""You are {agent_config['name']}, participating in a formal debate. {agent_config['behavior']} Keep your responses between 50-100 words and address your opponent's points directly."""
        return base_prompt
    
    def create_proposition_agents(self) -> List[Agent]:
        """Create all proposition agents from config"""
        if self._proposition_agents is None:
            self._proposition_agents = [
                self._create_agent_from_config(agent_config, "proposition_debater")
                for agent_config in self.proposition_configs
            ]
        return self._proposition_agents
    
    def create_opposition_agent(self) -> Agent:
        """Create opposition agent from config"""
        if self._opposition_agent is None:
            self._opposition_agent = self._create_agent_from_config(
                self.opposition_config,
                "opposition_debater"
            )
        return self._opposition_agent
    
    def create_moderator_agent(self) -> Agent:
        """Create moderator agent from config"""
        if self._moderator_agent is None:
            self._moderator_agent = self._create_agent_from_config(
                self.moderator_config,
                "moderator"
            )
        return self._moderator_agent
    
    def get_all_agents(self) -> dict:
        """Get all agents organized by type"""
        return {
            "proposition": self.create_proposition_agents(),
            "opposition": self.create_opposition_agent(),
            "moderator": self.create_moderator_agent()
        }
    
    def select_random_proposition(self, exclude_id: Optional[str] = None) -> Agent:
        """Randomly select a proposition agent, optionally excluding one"""
        agents = self.create_proposition_agents()
        
        if exclude_id:
            available_agents = [a for a in agents if a.agent_id != exclude_id]
        else:
            available_agents = agents
        
        if not available_agents:
            raise ValueError("No available proposition agents to select")
        
        return random.choice(available_agents)
    
    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Get specific agent by ID"""
        all_agents = (
            self.create_proposition_agents() + 
            [self.create_opposition_agent()] + 
            [self.create_moderator_agent()]
        )
        
        for agent in all_agents:
            if agent.agent_id == agent_id:
                return agent
        
        raise ValueError(f"Agent with ID '{agent_id}' not found")
    
    def get_agent_info(self) -> dict:
        """Get information about all configured agents"""
        return {
            "total_agents": config.get_agent_count()['total'],
            "proposition_count": config.get_agent_count()['proposition'],
            "proposition_agents": [
                {
                    "id": a['id'],
                    "name": a['name'],
                    "personality": a['personality_type'],
                    "icon": a.get('icon')
                }
                for a in self.proposition_configs
            ],
            "opposition": {
                "id": self.opposition_config['id'],
                "name": self.opposition_config['name'],
                "personality": self.opposition_config['personality_type'],
                "icon": self.opposition_config.get('icon')
            },
            "moderator": {
                "id": self.moderator_config['id'],
                "name": self.moderator_config['name'],
                "personality": self.moderator_config['personality_type']
            }
        }


# Global factory instance
agent_factory = AgentFactory()

