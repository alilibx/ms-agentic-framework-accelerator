"""Reusable Agent Definitions.

This package automatically discovers and creates agents from YAML configurations.
All .yaml files in the agents/ directory are automatically loaded.

Just add a new YAML file and it's immediately available!
"""

from .agent_factory import AgentFactory
import logging
import os

logger = logging.getLogger(__name__)

# Suppress verbose logging during discovery
os.environ['AGENT_DISCOVERY_QUIET'] = 'true'

# Create factory and auto-discover all agents
_factory = AgentFactory()
_discovered_agents = _factory.discover_all_agents()

# Export all discovered agents dynamically
# This makes them available as: from agents import weather_agent, stock_agent, etc.
globals().update(_discovered_agents)

# Build __all__ dynamically
__all__ = list(_discovered_agents.keys()) + ["AgentFactory", "get_all_agents", "get_discovery_data"]


def get_all_agents() -> dict:
    """Get all discovered agents.

    Returns:
        Dictionary mapping agent names to ChatAgent instances
    """
    return _discovered_agents.copy()


def get_discovery_data() -> dict:
    """Get discovery metadata for startup logging.

    Returns:
        Dictionary with tools_by_domain, agents, and agent_tools_map
    """
    from tools import ToolRegistry

    registry = ToolRegistry()

    # Get tools by domain
    tools_by_domain = {}
    for tool_id, tool_data in registry._tools.items():
        domain = tool_data['metadata'].get('domain', 'general')
        if domain not in tools_by_domain:
            tools_by_domain[domain] = []
        tools_by_domain[domain].append(tool_id)

    return {
        'tools_by_domain': tools_by_domain,
        'agents': _discovered_agents,
        'agent_tools_map': _factory.agent_tools_map,  # Map of agent_id -> tools
    }
