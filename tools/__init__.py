"""Dynamic Tool Library with Auto-Discovery.

This package provides a plugin-based tool system where tools are automatically
discovered from the filesystem using decorators.

Usage:
    from tools import ToolRegistry
    from tools._decorators import tool

    # Mark functions as tools
    @tool(domain="weather", tags=["forecast"])
    def my_tool():
        pass

    # Tools are automatically discovered and registered
    registry = ToolRegistry()
    all_tools = registry.list_all_tools()
"""

import logging
from tools._decorators import tool, get_tool_metadata, is_tool
from tools._registry import ToolRegistry
from tools._loader import ToolLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Auto-discover and register tools on import
logger.info("Initializing tool library...")

_registry = ToolRegistry()
_loader = ToolLoader()

# Discover tools (will happen when tools submodules are imported)
logger.info("Tool library ready for discovery")

__all__ = [
    "tool",
    "get_tool_metadata",
    "is_tool",
    "ToolRegistry",
    "ToolLoader",
]
