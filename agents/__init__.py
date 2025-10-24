"""Reusable Agent Definitions.

This package automatically discovers and creates agents from YAML configurations.
All .yaml files in the agents/ directory are automatically loaded.

Just add a new YAML file and it's immediately available!
"""

from .agent_factory import AgentFactory
import logging

logger = logging.getLogger(__name__)

# Create factory and auto-discover all agents
_factory = AgentFactory()
_discovered_agents = _factory.discover_all_agents()

# Export all discovered agents dynamically
# This makes them available as: from agents import weather_agent, stock_agent, etc.
globals().update(_discovered_agents)

# Build __all__ dynamically
__all__ = list(_discovered_agents.keys()) + ["AgentFactory", "get_all_agents"]


def get_all_agents() -> dict:
    """Get all discovered agents.

    Returns:
        Dictionary mapping agent names to ChatAgent instances
    """
    return _discovered_agents.copy()
