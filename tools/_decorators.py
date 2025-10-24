"""Tool decorator for dynamic tool registration.

This module provides the @tool decorator that marks functions as discoverable tools
that can be automatically registered with agents and MCP servers.
"""

from typing import Callable, Optional
from functools import wraps
import inspect
import logging

logger = logging.getLogger(__name__)


def tool(
    domain: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    mock: bool = False,
    requires_api_key: Optional[str] = None,
):
    """Decorator to register a function as a discoverable tool.

    Usage:
        @tool(domain="weather", tags=["forecast"])
        def get_forecast(location: str) -> str:
            '''Get weather forecast.'''
            return f"Forecast for {location}"

    Args:
        domain: The domain this tool belongs to (e.g., "weather", "stock")
        name: Optional custom name (defaults to function name)
        description: Optional description (defaults to docstring)
        tags: List of searchable tags for tool discovery
        mock: Whether this is a mock implementation
        requires_api_key: Name of required environment variable for API key

    Returns:
        Decorated function with _tool_metadata attribute
    """
    if tags is None:
        tags = []

    def decorator(func: Callable) -> Callable:
        # Get function signature for validation
        sig = inspect.signature(func)

        # Extract description from docstring if not provided
        func_description = description
        if func_description is None:
            func_description = func.__doc__ or f"{func.__name__} function"
            func_description = func_description.strip()

        # Attach metadata to function
        func._tool_metadata = {
            "domain": domain,
            "name": name or func.__name__,
            "description": func_description,
            "tags": tags,
            "mock": mock,
            "requires_api_key": requires_api_key,
            "signature": sig,
            "module": func.__module__,
        }

        logger.debug(
            f"Decorated tool: {func._tool_metadata['name']} "
            f"in domain '{domain}'"
        )

        return func

    return decorator


def get_tool_metadata(func: Callable) -> Optional[dict]:
    """Extract tool metadata from a decorated function.

    Args:
        func: Function that may have been decorated with @tool

    Returns:
        Tool metadata dictionary or None if not decorated
    """
    return getattr(func, "_tool_metadata", None)


def is_tool(func: Callable) -> bool:
    """Check if a function is a decorated tool.

    Args:
        func: Function to check

    Returns:
        True if function has been decorated with @tool
    """
    return hasattr(func, "_tool_metadata")
