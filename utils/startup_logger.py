"""Beautiful startup logging for the Multi-Agent System.

This module provides enhanced, colorful, and organized logging for system startup.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StartupLogger:
    """Enhanced logger for beautiful startup output."""

    # Color codes (ANSI)
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Emojis
    ROCKET = "🚀"
    CHECK = "✅"
    TOOLS = "🛠️ "
    AGENT = "🤖"
    CALENDAR = "📅"
    EMAIL = "📧"
    STOCK = "📈"
    WEATHER = "🌤️"
    LINK = "🔗"
    WARNING = "⚠️ "
    INFO = "ℹ️ "
    SPARKLES = "✨"
    PACKAGE = "📦"

    @staticmethod
    def _colorize(text: str, color: str, bold: bool = False) -> str:
        """Add color to text."""
        prefix = StartupLogger.BOLD if bold else ""
        return f"{prefix}{color}{text}{StartupLogger.RESET}"

    @staticmethod
    def print_header():
        """Print beautiful startup header."""
        width = 80
        print("\n" + "=" * width)
        title = f"{StartupLogger.ROCKET}  Multi-Agent System Startup"
        print(StartupLogger._colorize(title.center(width), StartupLogger.BLUE, bold=True))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(StartupLogger._colorize(timestamp.center(width), StartupLogger.GRAY))
        print("=" * width + "\n")

    @staticmethod
    def print_section(title: str, emoji: str = ""):
        """Print a section header."""
        full_title = f"{emoji} {title}" if emoji else title
        print(StartupLogger._colorize(full_title, StartupLogger.CYAN, bold=True))
        print(StartupLogger._colorize("─" * 80, StartupLogger.GRAY))

    @staticmethod
    def print_tool_discovery(tools_by_domain: Dict[str, List[str]]):
        """Print tool discovery summary."""
        StartupLogger.print_section("Tool Discovery", StartupLogger.TOOLS)

        total_tools = sum(len(tools) for tools in tools_by_domain.values())
        print(f"\n{StartupLogger.PACKAGE} Discovered {StartupLogger._colorize(str(total_tools), StartupLogger.GREEN, bold=True)} tools across {StartupLogger._colorize(str(len(tools_by_domain)), StartupLogger.GREEN, bold=True)} domains\n")

        # Domain icons
        domain_icons = {
            "calendar": "📅",
            "email": "📧",
            "stock": "📈",
            "weather": "🌤️",
        }

        for domain, tools in sorted(tools_by_domain.items()):
            icon = domain_icons.get(domain, "🔧")
            domain_name = StartupLogger._colorize(domain.title(), StartupLogger.BLUE, bold=True)
            count = StartupLogger._colorize(f"({len(tools)} tools)", StartupLogger.GREEN)
            print(f"  {icon}  {domain_name} {count}")

            # Show first 3 tools, then "and X more..."
            for i, tool in enumerate(sorted(tools)):
                if i < 3:
                    tool_name = tool.split('.')[-1] if '.' in tool else tool
                    print(f"     {StartupLogger._colorize('•', StartupLogger.GRAY)} {tool_name}")

            if len(tools) > 3:
                more = len(tools) - 3
                print(f"     {StartupLogger._colorize(f'... and {more} more', StartupLogger.GRAY)}")
            print()

    @staticmethod
    def print_agent_discovery(agents: Dict[str, Any], tools_by_domain: Dict[str, List[str]], agent_tools_map: Dict[str, List[Any]] = None):
        """Print agent discovery with tool mapping."""
        StartupLogger.print_section("Agent Discovery", StartupLogger.AGENT)

        print(f"\n{StartupLogger.SPARKLES} Discovered {StartupLogger._colorize(str(len(agents)), StartupLogger.GREEN, bold=True)} agents\n")

        # Agent icons
        agent_icons = {
            "calendar": "📅",
            "email": "📧",
            "stock": "📈",
            "weather": "🌤️",
        }

        for agent_id, agent in agents.items():
            # Determine icon
            icon = "🤖"
            for keyword, emoji in agent_icons.items():
                if keyword in agent_id.lower():
                    icon = emoji
                    break

            # Agent name
            agent_name = StartupLogger._colorize(agent.name, StartupLogger.BLUE, bold=True)

            # Get tool count from agent_tools_map
            tool_count = 0
            if agent_tools_map and agent_id in agent_tools_map:
                tool_count = len(agent_tools_map[agent_id])

            tools_text = StartupLogger._colorize(f"({tool_count} tools)", StartupLogger.GREEN)

            print(f"  {icon}  {agent_name} {tools_text}")

            # Show agent's model provider
            if hasattr(agent, 'chat_client'):
                model_info = "OpenRouter" if "openrouter" in str(type(agent.chat_client)).lower() else "Azure"
                provider_text = StartupLogger._colorize(f"Provider: {model_info}", StartupLogger.GRAY)
                print(f"      {provider_text}")

            print()

    @staticmethod
    def print_agent_tool_mapping(agents: Dict[str, Any], agent_tools_map: Dict[str, List[Any]] = None):
        """Print detailed agent-to-tool mapping."""
        StartupLogger.print_section("Agent → Tool Mapping", StartupLogger.LINK)

        print()
        for agent_id, agent in agents.items():
            # Determine icon
            icon = "🤖"
            if "calendar" in agent_id.lower():
                icon = "📅"
            elif "email" in agent_id.lower():
                icon = "📧"
            elif "stock" in agent_id.lower():
                icon = "📈"
            elif "weather" in agent_id.lower():
                icon = "🌤️"

            agent_name = StartupLogger._colorize(agent.name, StartupLogger.CYAN, bold=True)
            print(f"  {icon}  {agent_name}")

            # Get tools from agent_tools_map
            agent_tools = agent_tools_map.get(agent_id) if agent_tools_map else None

            if agent_tools:
                # Group tools by domain
                tools_by_domain = {}
                for tool in agent_tools:
                    tool_name = tool.__name__ if hasattr(tool, '__name__') else str(tool)

                    # Extract domain from tool metadata
                    domain = "general"
                    if hasattr(tool, '_tool_metadata'):
                        domain = tool._tool_metadata.get('domain', 'general')

                    if domain not in tools_by_domain:
                        tools_by_domain[domain] = []
                    tools_by_domain[domain].append(tool_name)

                # Print tools by domain
                for domain, tools in sorted(tools_by_domain.items()):
                    domain_text = StartupLogger._colorize(f"{domain}:", StartupLogger.BLUE)
                    tools_text = StartupLogger._colorize(f"{', '.join(tools[:3])}", StartupLogger.WHITE)
                    if len(tools) > 3:
                        tools_text += StartupLogger._colorize(f" (+{len(tools)-3} more)", StartupLogger.GRAY)
                    print(f"      {domain_text} {tools_text}")
            else:
                print(f"      {StartupLogger._colorize('No tools', StartupLogger.GRAY)}")

            print()

    @staticmethod
    def print_warnings(warnings: List[str]):
        """Print warnings section."""
        if not warnings:
            return

        StartupLogger.print_section("Warnings", StartupLogger.WARNING)
        print()
        for warning in warnings:
            print(f"  {StartupLogger.WARNING} {StartupLogger._colorize(warning, StartupLogger.YELLOW)}")
        print()

    @staticmethod
    def print_footer(url: str = "http://localhost:8080", agent_count: int = 0):
        """Print startup footer with URL."""
        print("=" * 80)

        # Status
        status = StartupLogger._colorize("✓ READY", StartupLogger.GREEN, bold=True)
        print(f"\n  {status}  System initialized successfully!\n")

        # URL
        url_text = StartupLogger._colorize(url, StartupLogger.CYAN, bold=True)
        print(f"  🌐  DevUI: {url_text}")

        # Stats
        agents_text = StartupLogger._colorize(f"{agent_count} agents", StartupLogger.GREEN)
        print(f"  📊  Active: {agents_text}")

        # Tips
        print(f"\n  {StartupLogger.SPARKLES}  {StartupLogger._colorize('Tip:', StartupLogger.GRAY)} Drop a YAML file in agents/ to add a new agent!")

        print("\n" + "=" * 80 + "\n")

    @staticmethod
    def print_startup_summary(tools_by_domain: Dict[str, List[str]], agents: Dict[str, Any], agent_tools_map: Dict[str, List[Any]] = None, warnings: List[str] = None):
        """Print complete startup summary."""
        StartupLogger.print_header()
        StartupLogger.print_tool_discovery(tools_by_domain)
        StartupLogger.print_agent_discovery(agents, tools_by_domain, agent_tools_map)
        StartupLogger.print_agent_tool_mapping(agents, agent_tools_map)

        if warnings:
            StartupLogger.print_warnings(warnings)

        StartupLogger.print_footer(agent_count=len(agents))
