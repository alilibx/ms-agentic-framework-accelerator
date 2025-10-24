"""Dynamic tool registry for managing discovered tools.

This module provides a singleton registry that stores all discovered tools
and provides methods for filtering and retrieving them.
"""

from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all discovered tools.

    This is a singleton class that maintains a registry of all tools
    decorated with @tool decorator. It provides methods for:
    - Registering tools
    - Querying tools by domain, tags, or ID
    - Listing all available tools

    Example:
        registry = ToolRegistry()
        registry.register_tool("weather.get_forecast", func, metadata)
        weather_tools = registry.get_tools_by_domain("weather")
    """

    _instance = None
    _tools = {}
    _initialized = False

    def __new__(cls):
        """Ensure only one instance of the registry exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the registry (only happens once due to singleton)."""
        if not ToolRegistry._initialized:
            ToolRegistry._tools = {}
            ToolRegistry._initialized = True
            logger.info("Tool registry initialized")

    def register_tool(self, tool_id: str, func: Callable, metadata: dict):
        """Register a tool in the registry.

        Args:
            tool_id: Unique identifier for the tool (e.g., "weather.get_forecast")
            func: The callable function
            metadata: Tool metadata dictionary containing domain, tags, etc.
        """
        self._tools[tool_id] = {"function": func, "metadata": metadata}
        logger.debug(f"Registered tool: {tool_id}")

    def get_tools_by_domain(self, domain: str) -> list:
        """Get all tools for a specific domain.

        Args:
            domain: The domain to filter by (e.g., "weather", "stock")

        Returns:
            List of tool dictionaries matching the domain
        """
        tools = [
            tool
            for tool_id, tool in self._tools.items()
            if tool["metadata"]["domain"] == domain
        ]
        logger.info(f"Found {len(tools)} tools for domain '{domain}'")
        return tools

    def get_tools_by_tags(self, tags: list[str]) -> list:
        """Get tools matching any of the specified tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of tool dictionaries matching any of the tags
        """
        matching_tools = [
            tool
            for tool in self._tools.values()
            if any(tag in tool["metadata"]["tags"] for tag in tags)
        ]
        logger.debug(f"Found {len(matching_tools)} tools matching tags: {tags}")
        return matching_tools

    def get_tool(self, tool_id: str) -> Optional[dict]:
        """Get a specific tool by its ID.

        Args:
            tool_id: The unique tool identifier

        Returns:
            Tool dictionary or None if not found
        """
        tool = self._tools.get(tool_id)
        if tool is None:
            logger.warning(f"Tool not found: {tool_id}")
        return tool

    def list_all_tools(self) -> dict:
        """Return all registered tools.

        Returns:
            Dictionary of all tools with tool_id as keys
        """
        return self._tools.copy()

    def list_domains(self) -> list[str]:
        """List all available domains.

        Returns:
            Sorted list of unique domain names
        """
        domains = set(tool["metadata"]["domain"] for tool in self._tools.values())
        return sorted(domains)

    def list_tool_ids(self) -> list[str]:
        """List all registered tool IDs.

        Returns:
            Sorted list of tool IDs
        """
        return sorted(self._tools.keys())

    def count_tools(self, domain: Optional[str] = None) -> int:
        """Count the number of registered tools.

        Args:
            domain: Optional domain filter

        Returns:
            Number of tools (all or for specific domain)
        """
        if domain is None:
            return len(self._tools)
        return len(self.get_tools_by_domain(domain))

    def clear(self):
        """Clear all registered tools.

        This is useful for testing or when reloading tools.
        """
        count = len(self._tools)
        self._tools.clear()
        logger.info(f"Cleared {count} tools from registry")

    def reload(self):
        """Trigger a reload of all tools.

        This clears the registry and re-runs tool discovery.
        """
        logger.info("Reloading tool registry...")
        self.clear()

        # Import loader here to avoid circular dependency
        from tools._loader import ToolLoader

        loader = ToolLoader()
        discovered = loader.discover_tools()

        for tool_id, tool_data in discovered.items():
            self.register_tool(
                tool_id, tool_data["function"], tool_data["metadata"]
            )

        logger.info(f"Reload complete: {len(self._tools)} tools registered")

    def get_summary(self) -> dict:
        """Get a summary of the registry state.

        Returns:
            Dictionary with registry statistics
        """
        domains = self.list_domains()
        return {
            "total_tools": len(self._tools),
            "domains": domains,
            "tools_per_domain": {
                domain: self.count_tools(domain) for domain in domains
            },
        }

    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"<ToolRegistry: {len(self._tools)} tools across {len(self.list_domains())} domains>"
