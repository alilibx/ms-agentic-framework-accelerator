"""Agent Factory - Dynamically build agents from YAML configuration.

This module provides the AgentFactory class that can create ChatAgent instances
from declarative YAML configuration files. Agents automatically discover and
attach tools based on domain and tag filters specified in the config.
"""

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from tools import ToolRegistry, ToolLoader
from pathlib import Path
import yaml
import logging
import os
from dotenv import load_dotenv
from .tool_context import inject_tool_context

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import OpenAI chat client (may not be available in all versions)
try:
    from agent_framework.openai import OpenAIChatClient
    OPENAI_CLIENT_AVAILABLE = True
except ImportError:
    OPENAI_CLIENT_AVAILABLE = False
    logger.warning("OpenAIChatClient not available - OpenRouter/OpenAI support disabled")


class AgentFactory:
    """Build agents dynamically from YAML configuration.

    The factory reads YAML config files that specify:
    - Agent name and description
    - Tool domains and tags (for auto-discovery)
    - Agent instructions (prompts)
    - Model configuration

    Tools are automatically discovered and attached based on the config.

    Example:
        factory = AgentFactory()
        weather_agent = factory.from_yaml("agents/weather_agent.yaml")
        # Agent now has ALL weather domain tools automatically!
    """

    def __init__(self):
        """Initialize the agent factory."""
        self.registry = self._ensure_tools_loaded()
        self.agent_tools_map = {}  # Track tools for each agent
        logger.info("AgentFactory initialized")

    def _ensure_tools_loaded(self) -> ToolRegistry:
        """Ensure all tools are discovered and loaded into registry.

        Returns:
            ToolRegistry instance with all tools loaded
        """
        registry = ToolRegistry()

        # Check if tools are already loaded
        if registry.count_tools() == 0:
            logger.info("No tools in registry, running discovery...")
            loader = ToolLoader()
            discovered = loader.discover_tools()

            # Register all discovered tools
            for tool_id, tool_data in discovered.items():
                registry.register_tool(
                    tool_id,
                    tool_data["function"],
                    tool_data["metadata"]
                )

            logger.info(f"Loaded {len(discovered)} tools into registry")
        else:
            logger.info(f"Registry already contains {registry.count_tools()} tools")

        return registry

    def from_yaml(self, config_path: str | Path) -> ChatAgent:
        """Create an agent from a YAML configuration file.

        Args:
            config_path: Path to YAML config file

        Returns:
            ChatAgent instance with auto-discovered tools

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid

        Example:
            agent = factory.from_yaml("agents/weather_agent.yaml")
        """
        config_file = Path(config_path)
        quiet_mode = os.getenv('AGENT_DISCOVERY_QUIET') == 'true'

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if not quiet_mode:
            logger.info(f"Loading agent from: {config_path}")

        # Load YAML configuration
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Discover tools based on config
        tool_functions = self._discover_tools_for_agent(config)

        # Build model client
        chat_client = self._build_chat_client(config)

        # Inject dynamic tool context into instructions
        base_instructions = config["instructions"]
        enhanced_instructions = inject_tool_context(
            base_instructions,
            tool_functions,
            compact=config.get("compact_tool_context", False)
        )

        # Create agent
        agent = ChatAgent(
            name=config["name"],
            description=config["description"],
            instructions=enhanced_instructions,
            tools=tool_functions,
            chat_client=chat_client,
        )

        # Store tools for this agent (for discovery reporting)
        agent_id = config_file.stem  # e.g., "weather_agent"
        self.agent_tools_map[agent_id] = tool_functions

        if not quiet_mode:
            logger.info(
                f"✅ Created agent '{config['name']}' with {len(tool_functions)} tools"
            )

        return agent

    def _discover_tools_for_agent(self, config: dict) -> list:
        """Discover tools based on agent configuration.

        Args:
            config: Parsed YAML configuration

        Returns:
            List of tool functions to attach to agent
        """
        quiet_mode = os.getenv('AGENT_DISCOVERY_QUIET') == 'true'
        tool_functions = []
        tool_count_by_source = {}

        # Get tools by domain
        for domain in config.get("tool_domains", []):
            domain_tools = self.registry.get_tools_by_domain(domain)
            if not quiet_mode:
                logger.info(f"Found {len(domain_tools)} tools for domain '{domain}'")
            for tool in domain_tools:
                if tool["function"] not in tool_functions:
                    tool_functions.append(tool["function"])
                    tool_count_by_source[f"domain:{domain}"] = (
                        tool_count_by_source.get(f"domain:{domain}", 0) + 1
                    )

        # Get tools by tags (if specified)
        if "tool_tags" in config:
            tag_tools = self.registry.get_tools_by_tags(config["tool_tags"])
            for tool in tag_tools:
                if tool["function"] not in tool_functions:
                    tool_functions.append(tool["function"])
                    tool_count_by_source["tags"] = (
                        tool_count_by_source.get("tags", 0) + 1
                    )

        # Filter excluded tools
        excluded = config.get("exclude_tools", [])
        if excluded:
            original_count = len(tool_functions)
            tool_functions = [
                func
                for func in tool_functions
                if getattr(func, "_tool_metadata", {}).get("name") not in excluded
            ]
            removed = original_count - len(tool_functions)
            if removed > 0 and not quiet_mode:
                logger.info(f"Excluded {removed} tools")

        # Log discovery results
        if not quiet_mode:
            logger.info(f"Tool discovery results:")
            for source, count in tool_count_by_source.items():
                logger.info(f"  - {count} tools from {source}")

        return tool_functions

    def _build_chat_client(self, config: dict):
        """Build the chat client from config.

        Supports multiple providers with automatic fallback:
        - azure: Azure OpenAI (default)
        - openrouter: OpenRouter API
        - openai: Direct OpenAI API

        If the primary provider fails, automatically falls back to available alternatives.

        Args:
            config: Parsed YAML configuration

        Returns:
            Configured chat client
        """
        model_config = config.get("model", {})

        # Get provider list (supports both single provider and fallback list)
        providers = model_config.get("providers", [])
        if not providers:
            # Legacy support: single provider field
            primary_provider = model_config.get("provider", "azure").lower()
            providers = [primary_provider]

        # Try each provider in order until one succeeds
        quiet_mode = os.getenv('AGENT_DISCOVERY_QUIET') == 'true'
        last_error = None
        for provider in providers:
            try:
                if not quiet_mode:
                    logger.info(f"Building chat client for provider: {provider}")

                if provider == "azure":
                    return self._build_azure_client(model_config)
                elif provider == "openrouter":
                    return self._build_openrouter_client(model_config)
                elif provider == "openai":
                    return self._build_openai_client(model_config)
                else:
                    logger.warning(f"Unsupported provider: {provider}, trying next...")
                    continue

            except Exception as e:
                last_error = e
                logger.warning(f"Provider '{provider}' failed: {e}")
                if len(providers) > 1:
                    logger.info(f"Trying next provider...")
                continue

        # If all providers failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise ValueError(f"No valid providers configured")

    def _build_azure_client(self, model_config: dict) -> AzureOpenAIChatClient:
        """Build Azure OpenAI chat client.

        Args:
            model_config: Model configuration from YAML

        Returns:
            Configured AzureOpenAIChatClient
        """
        credential_type = model_config.get("credential_type", "azure_cli")

        if credential_type == "azure_cli":
            credential = AzureCliCredential()
        elif credential_type == "api_key":
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY not found in environment")
            # Note: agent_framework may need to support api_key auth
            credential = api_key
        else:
            raise ValueError(f"Unsupported credential type: {credential_type}")

        client = AzureOpenAIChatClient(
            endpoint=model_config.get("endpoint", os.getenv("AZURE_OPENAI_ENDPOINT")),
            deployment_name=model_config.get("deployment", os.getenv("AZURE_OPENAI_DEPLOYMENT")),
            credential=credential,
        )

        return client

    def _build_openrouter_client(self, model_config: dict):
        """Build OpenRouter chat client.

        Args:
            model_config: Model configuration from YAML

        Returns:
            Configured OpenRouter-compatible client
        """
        if not OPENAI_CLIENT_AVAILABLE:
            raise ImportError(
                "OpenAIChatClient not available in agent_framework. "
                "Please upgrade: pip install --upgrade --pre agent-framework"
            )

        api_key = model_config.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or config")

        base_url = model_config.get("base_url", os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
        model_id = model_config.get("model", os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo"))

        # Create OpenAI chat client pointing to OpenRouter
        client = OpenAIChatClient(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
        )

        quiet_mode = os.getenv('AGENT_DISCOVERY_QUIET') == 'true'
        if not quiet_mode:
            logger.info(f"OpenRouter client created with model: {model_id}")

        return client

    def _build_openai_client(self, model_config: dict):
        """Build direct OpenAI chat client.

        Args:
            model_config: Model configuration from YAML

        Returns:
            Configured OpenAI client
        """
        if not OPENAI_CLIENT_AVAILABLE:
            raise ImportError(
                "OpenAIChatClient not available in agent_framework. "
                "Please upgrade: pip install --upgrade --pre agent-framework"
            )

        api_key = model_config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment or config")

        model_id = model_config.get("model", os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"))

        # Create OpenAI chat client
        client = OpenAIChatClient(
            model_id=model_id,
            api_key=api_key,
        )

        logger.info(f"OpenAI client created with model: {model_id}")

        return client

    @staticmethod
    def list_available_configs(configs_dir: str | Path = "agents") -> list[str]:
        """List all available agent YAML configurations.

        Args:
            configs_dir: Directory containing agent configs

        Returns:
            List of available config names (without .yaml extension)

        Example:
            configs = AgentFactory.list_available_configs()
            # ['weather_agent', 'stock_agent']
        """
        config_path = Path(configs_dir)

        if not config_path.exists():
            logger.warning(f"Config directory not found: {configs_dir}")
            return []

        configs = [
            f.stem
            for f in config_path.glob("*.yaml")
            if f.stem != "agent_config" and not f.stem.startswith("_")
        ]

        return sorted(configs)

    def discover_all_agents(self, configs_dir: str | Path = "agents") -> dict[str, ChatAgent]:
        """Automatically discover and create all agents from YAML configs.

        This method scans the agents directory and creates an agent for each
        YAML file found. Agents are cached to avoid recreating them.

        Args:
            configs_dir: Directory containing agent configs

        Returns:
            Dictionary mapping agent names to ChatAgent instances

        Example:
            factory = AgentFactory()
            agents = factory.discover_all_agents()
            # {'weather_agent': <ChatAgent>, 'stock_agent': <ChatAgent>, ...}
        """
        quiet_mode = os.getenv('AGENT_DISCOVERY_QUIET') == 'true'
        configs = self.list_available_configs(configs_dir)
        agents = {}

        if not quiet_mode:
            logger.info(f"🔍 Discovering agents in {configs_dir}/")

        for config_name in configs:
            try:
                config_path = Path(configs_dir) / f"{config_name}.yaml"
                agent = self.from_yaml(config_path)
                agents[config_name] = agent
                if not quiet_mode:
                    logger.info(f"   ✅ {config_name}: {agent.name}")
            except Exception as e:
                logger.error(f"   ❌ {config_name}: Failed to load - {e}")

        if not quiet_mode:
            logger.info(f"📊 Discovered {len(agents)} agents")

        return agents

    def reload_tools(self):
        """Reload all tools from the filesystem.

        This is useful for hot-reloading when tools are added or modified.
        """
        logger.info("Reloading tools...")
        self.registry.reload()
        logger.info(f"Tools reloaded: {self.registry.count_tools()} total")

    def get_registry_summary(self) -> dict:
        """Get a summary of the current tool registry state.

        Returns:
            Dictionary with registry statistics
        """
        return self.registry.get_summary()
