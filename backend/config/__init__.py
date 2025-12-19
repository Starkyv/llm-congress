import json
import os
from typing import Dict, List, Any


class AgentConfig:
    """Loads and validates agent configuration"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Get the directory where this file is located
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(config_dir, "agent_config.json")
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _validate_config(self):
        """Validate configuration structure"""
        required_keys = ['debate_config', 'proposition_agents', 'opposition_agent', 'moderator_agent']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate at least one proposition agent
        if not self.config['proposition_agents']:
            raise ValueError("At least one proposition agent is required")
        
        # Validate agent structures
        for agent in self.config['proposition_agents']:
            self._validate_agent_structure(agent, "proposition")
        
        self._validate_agent_structure(self.config['opposition_agent'], "opposition")
        self._validate_agent_structure(self.config['moderator_agent'], "moderator")
    
    def _validate_agent_structure(self, agent: Dict, agent_type: str):
        """Validate individual agent configuration"""
        required_fields = ['id', 'name', 'personality_type', 'behavior']
        for field in required_fields:
            if field not in agent:
                raise ValueError(f"Missing required field '{field}' in {agent_type} agent")
    
    def get_debate_config(self) -> Dict[str, Any]:
        """Get debate configuration"""
        return self.config['debate_config']
    
    def get_proposition_agents_config(self) -> List[Dict[str, Any]]:
        """Get list of proposition agent configurations"""
        return self.config['proposition_agents']
    
    def get_opposition_agent_config(self) -> Dict[str, Any]:
        """Get opposition agent configuration"""
        return self.config['opposition_agent']
    
    def get_moderator_agent_config(self) -> Dict[str, Any]:
        """Get moderator agent configuration"""
        return self.config['moderator_agent']
    
    def get_agent_count(self) -> Dict[str, int]:
        """Get count of each agent type"""
        return {
            "proposition": len(self.config['proposition_agents']),
            "opposition": 1,
            "moderator": 1,
            "total": len(self.config['proposition_agents']) + 2
        }


# Global config instance
config = AgentConfig()

