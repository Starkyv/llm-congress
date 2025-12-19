"""
Agents Module

Provides access to dynamically created agents from configuration.
"""

from .agent_factory import agent_factory


def get_all_proposition_agents():
    """Get all proposition agents from config"""
    return agent_factory.create_proposition_agents()


def get_opposition_agent():
    """Get opposition agent from config"""
    return agent_factory.create_opposition_agent()


def get_moderator_agent():
    """Get moderator agent from config"""
    return agent_factory.create_moderator_agent()


def get_all_agents():
    """Get all agents organized by type"""
    return agent_factory.get_all_agents()


def select_random_proposition(exclude_id=None):
    """Select random proposition agent"""
    return agent_factory.select_random_proposition(exclude_id)


def get_agent_info():
    """Get information about configured agents"""
    return agent_factory.get_agent_info()


__all__ = [
    'get_all_proposition_agents',
    'get_opposition_agent',
    'get_moderator_agent',
    'get_all_agents',
    'select_random_proposition',
    'get_agent_info',
    'agent_factory'
]

