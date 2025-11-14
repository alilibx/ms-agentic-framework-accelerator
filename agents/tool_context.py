"""Dynamic tool context generation for agents.

This module provides utilities to automatically generate tool capability
descriptions from tool metadata, eliminating the need to manually maintain
tool lists in agent YAML configurations.
"""

from typing import List, Dict, Any
from tools import ToolRegistry
import logging

logger = logging.getLogger(__name__)


class ToolContextGenerator:
    """Generates dynamic tool context from registry metadata."""

    def __init__(self, registry: ToolRegistry = None):
        """Initialize the generator.

        Args:
            registry: ToolRegistry instance. If None, uses singleton.
        """
        self.registry = registry or ToolRegistry()

    def generate_tool_context(self, tool_functions: List[Any]) -> str:
        """Generate comprehensive tool documentation from tool functions.

        Args:
            tool_functions: List of tool functions attached to agent

        Returns:
            Formatted string describing all available tools
        """
        if not tool_functions:
            return ""

        # Group tools by domain
        tools_by_domain = self._group_by_domain(tool_functions)

        # Build context sections
        sections = ["## AVAILABLE TOOLS\n"]
        sections.append("You have access to the following tools:\n")

        for domain, tools in sorted(tools_by_domain.items()):
            sections.append(f"\n### {domain.upper()} TOOLS")

            for tool in tools:
                metadata = tool.get('metadata', {})
                name = metadata.get('name', 'Unknown')
                description = metadata.get('description', 'No description')

                # Format tool entry
                sections.append(f"- **{name}**: {description}")

        sections.append("\n## USAGE GUIDELINES\n")
        sections.append("- Use the appropriate tool based on the user's question")
        sections.append("- When asked about your capabilities or tools, mention ALL tools listed above from all domains")
        sections.append("- Always provide clear, well-formatted responses")
        sections.append("- If unsure which tool to use, ask the user for clarification")

        return "\n".join(sections)

    def generate_compact_context(self, tool_functions: List[Any]) -> str:
        """Generate compact tool listing for context efficiency.

        Args:
            tool_functions: List of tool functions attached to agent

        Returns:
            Compact formatted string listing tools
        """
        if not tool_functions:
            return ""

        tools_info = []
        for tool_func in tool_functions:
            metadata = getattr(tool_func, '_tool_metadata', {})
            if metadata:
                name = metadata.get('name', tool_func.__name__)
                description = metadata.get('description', '')
                tools_info.append(f"{name}: {description}")

        if not tools_info:
            return ""

        return "## Available Tools\n" + "\n".join(f"- {info}" for info in tools_info)

    def _group_by_domain(self, tool_functions: List[Any]) -> Dict[str, List[Dict]]:
        """Group tool functions by their domain.

        Args:
            tool_functions: List of tool functions

        Returns:
            Dictionary mapping domain -> list of tool metadata
        """
        grouped = {}

        for tool_func in tool_functions:
            # Get metadata from function attribute
            metadata = getattr(tool_func, '_tool_metadata', None)

            if metadata:
                domain = metadata.get('domain', 'general')

                if domain not in grouped:
                    grouped[domain] = []

                grouped[domain].append({
                    'function': tool_func,
                    'metadata': metadata
                })
            else:
                # Fallback for tools without metadata
                logger.warning(f"Tool {tool_func.__name__} missing metadata")
                if 'general' not in grouped:
                    grouped['general'] = []
                grouped['general'].append({
                    'function': tool_func,
                    'metadata': {
                        'name': tool_func.__name__,
                        'description': tool_func.__doc__ or 'No description',
                        'domain': 'general'
                    }
                })

        return grouped


def inject_tool_context(base_instructions: str, tool_functions: List[Any],
                        compact: bool = False) -> str:
    """Inject dynamic tool context into agent instructions.

    This function automatically appends tool capability information to
    agent instructions based on the tools attached to the agent.

    Args:
        base_instructions: Base agent instructions from YAML
        tool_functions: List of tool functions attached to agent
        compact: Use compact format to save tokens

    Returns:
        Enhanced instructions with tool context

    Example:
        >>> tools = [get_weather, get_forecast]
        >>> instructions = "You are a weather assistant."
        >>> enhanced = inject_tool_context(instructions, tools)
        >>> print(enhanced)
        You are a weather assistant.

        ## AVAILABLE TOOLS
        ...
    """
    generator = ToolContextGenerator()

    if compact:
        tool_context = generator.generate_compact_context(tool_functions)
    else:
        tool_context = generator.generate_tool_context(tool_functions)

    if not tool_context:
        return base_instructions

    # Combine base instructions with tool context
    separator = "\n\n" + "=" * 80 + "\n\n"
    return base_instructions + separator + tool_context
