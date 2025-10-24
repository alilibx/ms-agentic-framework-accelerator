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

logger = logging.getLogger(__name__)


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

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        logger.info(f"Loading agent from: {config_path}")

        # Load YAML configuration
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Discover tools based on config
        tool_functions = self._discover_tools_for_agent(config)

        # Build model client
        chat_client = self._build_chat_client(config)

        # Create agent
        agent = ChatAgent(
            name=config["name"],
            description=config["description"],
            instructions=config["instructions"],
            tools=tool_functions,
            chat_client=chat_client,
        )

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
        tool_functions = []
        tool_count_by_source = {}

        # Get tools by domain
        for domain in config.get("tool_domains", []):
            domain_tools = self.registry.get_tools_by_domain(domain)
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
            if removed > 0:
                logger.info(f"Excluded {removed} tools")

        # Log discovery results
        logger.info(f"Tool discovery results:")
        for source, count in tool_count_by_source.items():
            logger.info(f"  - {count} tools from {source}")

        return tool_functions

    def _build_chat_client(self, config: dict) -> AzureOpenAIChatClient:
        """Build the Azure OpenAI chat client from config.

        Args:
            config: Parsed YAML configuration

        Returns:
            Configured AzureOpenAIChatClient
        """
        model_config = config.get("model", {})

        # Build credential based on config
        credential_type = model_config.get("credential_type", "azure_cli")

        if credential_type == "azure_cli":
            credential = AzureCliCredential()
        else:
            raise ValueError(f"Unsupported credential type: {credential_type}")

        # Create client
        client = AzureOpenAIChatClient(
            endpoint=model_config.get("endpoint"),
            deployment_name=model_config.get("deployment"),
            credential=credential,
        )

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
        configs = self.list_available_configs(configs_dir)
        agents = {}

        logger.info(f"🔍 Discovering agents in {configs_dir}/")

        for config_name in configs:
            try:
                config_path = Path(configs_dir) / f"{config_name}.yaml"
                agent = self.from_yaml(config_path)
                agents[config_name] = agent
                logger.info(f"   ✅ {config_name}: {agent.name}")
            except Exception as e:
                logger.error(f"   ❌ {config_name}: Failed to load - {e}")

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
