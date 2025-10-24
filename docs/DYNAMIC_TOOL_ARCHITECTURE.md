# 🔌 Dynamic Tool Discovery & MCP Server - Implementation Plan

## 🎯 Core Concept: Plugin Architecture

**Goal**: Add a tool file → Agent automatically discovers it. No agent code changes needed.

### Key Principles:
1. **Decorator-based registration** - Mark functions with `@tool` decorator
2. **Automatic scanning** - Tools auto-discovered from filesystem
3. **Hot-reload support** - Add/update tools without restart
4. **Agent abstraction** - Agents are just prompts + domain filters

---

## 📁 Enhanced Project Structure

```
agentic-ms/
├── tools/                          # Plugin-based Tool Library
│   ├── __init__.py                # Auto-discovery engine
│   ├── _registry.py               # Dynamic tool registry
│   ├── _decorators.py             # @tool decorator
│   ├── _loader.py                 # Tool scanning & loading
│   │
│   ├── weather/
│   │   ├── current_weather.py     # Each tool = separate file
│   │   ├── forecast.py
│   │   └── weather_alerts.py      # Add new → auto-discovered!
│   │
│   ├── stock/
│   │   ├── stock_price.py
│   │   ├── stock_analysis.py
│   │   ├── stock_history.py
│   │   └── market_news.py         # Add new → auto-discovered!
│   │
│   └── common/
│       ├── formatters.py
│       └── validators.py
│
├── agents/
│   ├── __init__.py
│   ├── agent_config.yaml          # Declarative agent config (NEW)
│   ├── weather_agent.yaml         # Just prompts + tool domains
│   ├── stock_agent.yaml
│   └── agent_factory.py           # Builds agents from config
│
├── mcp_servers/
│   ├── server.py                  # Auto-exposes all registered tools
│   └── config.yaml
│
└── config/
    ├── tool_registry.yaml         # Optional: tool metadata
    └── .env
```

---

## 🔧 Implementation Details

### 1. Tool Decorator System

**File: `tools/_decorators.py`**
```python
from typing import Callable, Optional
from functools import wraps
import inspect

def tool(
    domain: str,                    # "weather", "stock", etc.
    name: Optional[str] = None,     # Auto-generated from function name
    description: Optional[str] = None,  # From docstring if not provided
    tags: list[str] = None,         # For filtering/search
    mock: bool = False,             # Is this a mock implementation?
    requires_api_key: Optional[str] = None,  # "OPENWEATHER_API_KEY"
):
    """Decorator to register a function as a discoverable tool."""
    def decorator(func: Callable):
        # Extract metadata
        func._tool_metadata = {
            "domain": domain,
            "name": name or func.__name__,
            "description": description or func.__doc__,
            "tags": tags or [],
            "mock": mock,
            "requires_api_key": requires_api_key,
            "signature": inspect.signature(func),
        }
        return func
    return decorator
```

**Usage Example:**
```python
# tools/weather/current_weather.py

@tool(
    domain="weather",
    description="Get current weather for a location",
    tags=["weather", "current", "temperature"],
    mock=True
)
def get_weather(location: str) -> str:
    """Get current weather conditions."""
    return f"Weather in {location}: Sunny, 22°C"
```

---

### 2. Auto-Discovery Engine

**File: `tools/_loader.py`**
```python
import importlib
import pkgutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ToolLoader:
    """Automatically discovers and loads tools from the tools directory."""

    def discover_tools(self, tools_dir: Path = None):
        """Scan tools directory and register all @tool decorated functions."""
        tools_dir = tools_dir or Path(__file__).parent
        discovered = {}

        # Walk through all Python files in tools/
        for module_info in pkgutil.walk_packages([str(tools_dir)]):
            if module_info.name.startswith('_'):
                continue  # Skip internal modules

            try:
                # Import module
                module = importlib.import_module(f"tools.{module_info.name}")

                # Find all @tool decorated functions
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, '_tool_metadata'):
                        metadata = attr._tool_metadata
                        tool_id = f"{metadata['domain']}.{metadata['name']}"
                        discovered[tool_id] = {
                            "function": attr,
                            "metadata": metadata
                        }
                        logger.info(f"Discovered tool: {tool_id}")
            except Exception as e:
                logger.error(f"Error loading module {module_info.name}: {e}")

        return discovered
```

---

### 3. Dynamic Tool Registry

**File: `tools/_registry.py`**
```python
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Central registry for all discovered tools."""

    _instance = None
    _tools = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_tool(self, tool_id: str, func: Callable, metadata: dict):
        """Register a tool."""
        self._tools[tool_id] = {
            "function": func,
            "metadata": metadata
        }
        logger.debug(f"Registered tool: {tool_id}")

    def get_tools_by_domain(self, domain: str) -> list:
        """Get all tools for a specific domain."""
        tools = [
            tool for tool_id, tool in self._tools.items()
            if tool['metadata']['domain'] == domain
        ]
        logger.info(f"Found {len(tools)} tools for domain '{domain}'")
        return tools

    def get_tools_by_tags(self, tags: list[str]) -> list:
        """Get tools matching any of the tags."""
        return [
            tool for tool in self._tools.values()
            if any(tag in tool['metadata']['tags'] for tag in tags)
        ]

    def get_tool(self, tool_id: str) -> Optional[dict]:
        """Get a specific tool by ID."""
        return self._tools.get(tool_id)

    def list_all_tools(self) -> dict:
        """Return all registered tools."""
        return self._tools

    def list_domains(self) -> list[str]:
        """List all available domains."""
        domains = set(tool['metadata']['domain'] for tool in self._tools.values())
        return sorted(domains)

    def clear(self):
        """Clear all registered tools (for testing or reload)."""
        self._tools.clear()
```

---

### 4. Declarative Agent Configuration

**File: `agents/weather_agent.yaml`**
```yaml
name: "Weather Assistant"
description: "Provides weather information and forecasts"

# Agent just declares what it needs - tools are auto-discovered!
tool_domains:
  - weather

tool_tags:
  - weather
  - forecast
  - temperature

instructions: |
  You are a weather assistant. You can provide current weather information
  and forecasts for any location. Always be helpful and provide detailed
  weather information when asked.

model:
  endpoint: "https://azure-openai-aueast.openai.azure.com/"
  deployment: "gpt-4o-moretpm"
  credential_type: "azure_cli"

# Optional: Exclude specific tools
exclude_tools:
  - weather.extreme_weather  # Maybe not ready yet

# Optional: Use real APIs if available
use_real_apis: false  # Set to true for production
```

---

### 5. Agent Factory (Dynamic Agent Builder)

**File: `agents/agent_factory.py`**
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from tools._registry import ToolRegistry
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AgentFactory:
    """Build agents dynamically from configuration."""

    @staticmethod
    def from_yaml(config_path: str) -> ChatAgent:
        """Create agent from YAML config."""
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file) as f:
            config = yaml.safe_load(f)

        registry = ToolRegistry()

        # Auto-discover tools based on domains and tags
        tool_functions = []

        # Get tools by domain
        for domain in config.get('tool_domains', []):
            domain_tools = registry.get_tools_by_domain(domain)
            tool_functions.extend([t['function'] for t in domain_tools])
            logger.info(f"Loaded {len(domain_tools)} tools from domain '{domain}'")

        # Get tools by tags (if specified)
        if 'tool_tags' in config:
            tag_tools = registry.get_tools_by_tags(config['tool_tags'])
            # Avoid duplicates
            existing_funcs = set(tool_functions)
            for tool in tag_tools:
                if tool['function'] not in existing_funcs:
                    tool_functions.append(tool['function'])

        # Filter excluded tools
        excluded = config.get('exclude_tools', [])
        if excluded:
            tool_functions = [
                func for func in tool_functions
                if getattr(func, '_tool_metadata', {}).get('name') not in excluded
            ]

        # Build model client
        model_config = config.get('model', {})
        chat_client = AzureOpenAIChatClient(
            endpoint=model_config.get('endpoint'),
            deployment_name=model_config.get('deployment'),
            credential=AzureCliCredential(),
        )

        # Build agent
        agent = ChatAgent(
            name=config['name'],
            description=config['description'],
            instructions=config['instructions'],
            tools=tool_functions,
            chat_client=chat_client,
        )

        logger.info(f"Created agent '{config['name']}' with {len(tool_functions)} tools")

        return agent

    @staticmethod
    def list_available_configs(configs_dir: str = "agents") -> list[str]:
        """List all available agent configurations."""
        config_path = Path(configs_dir)
        return [f.stem for f in config_path.glob("*.yaml") if f.stem != "agent_config"]
```

---

### 6. Usage Examples

#### Adding a New Tool (Zero Agent Changes!)

**Step 1: Create new tool file**
```python
# tools/weather/weather_alerts.py

from tools._decorators import tool

@tool(
    domain="weather",
    description="Get weather alerts for a location",
    tags=["weather", "alerts", "warnings"]
)
def get_weather_alerts(location: str, severity: str = "all") -> str:
    """Get active weather alerts and warnings."""
    # Implementation
    return f"No active alerts for {location}"
```

**Step 2: That's it!**
- Tool automatically discovered on next import
- Weather agent automatically has this new tool
- MCP server automatically exposes it

#### Using Agents

```python
from agents.agent_factory import AgentFactory

# Load agent from config - tools auto-attached
weather_agent = AgentFactory.from_yaml("agents/weather_agent.yaml")

# Agent has ALL weather domain tools automatically!
result = await weather_agent.run("What's the weather in NYC?")
```

---

### 7. MCP Server Auto-Exposure

**File: `mcp_servers/server.py`**
```python
from mcp.server import Server
from tools._registry import ToolRegistry
import logging

logger = logging.getLogger(__name__)

class DynamicMCPServer:
    """MCP server that auto-exposes all registered tools."""

    def __init__(self, server_name: str = "agentic-ms-server"):
        self.registry = ToolRegistry()
        self.server = Server(server_name)
        self._register_all_tools()
        logger.info(f"MCP Server '{server_name}' initialized")

    def _register_all_tools(self):
        """Automatically register all tools from registry."""
        all_tools = self.registry.list_all_tools()

        for tool_id, tool_data in all_tools.items():
            func = tool_data['function']
            metadata = tool_data['metadata']

            # MCP server auto-generates schema from type hints
            self.server.add_tool(
                name=tool_id,
                description=metadata['description'],
                function=func
            )
            logger.debug(f"Exposed tool via MCP: {tool_id}")

        logger.info(f"Registered {len(all_tools)} tools with MCP server")

    def reload_tools(self):
        """Hot-reload: Rediscover and re-register tools."""
        logger.info("Reloading tools...")
        self.registry.clear()
        from tools._loader import ToolLoader
        loader = ToolLoader()
        discovered = loader.discover_tools()

        for tool_id, tool_data in discovered.items():
            self.registry.register_tool(tool_id, tool_data['function'], tool_data['metadata'])

        self._register_all_tools()
        logger.info("Tools reloaded successfully")

    def start(self, transport: str = "stdio"):
        """Start the MCP server."""
        logger.info(f"Starting MCP server with {transport} transport...")
        self.server.run(transport)
```

---

## 🎨 Example Workflow

### Scenario: Adding Stock News Tool

**Before:**
```
Weather Agent: has weather tools
Stock Agent: has price, analysis, history
```

**Action: Create new file**
```python
# tools/stock/market_news.py

from tools._decorators import tool

@tool(domain="stock", tags=["news", "market"])
def get_market_news(symbol: str, limit: int = 5) -> str:
    """Get latest market news for a stock."""
    return f"Latest news for {symbol}..."
```

**After (Automatic!):**
```
Weather Agent: has weather tools (unchanged)
Stock Agent: NOW ALSO HAS market_news! (auto-discovered)
MCP Server: Exposes market_news (auto-registered)
```

**No code changes needed in:**
- ❌ stock_agent.py
- ❌ Agent configuration
- ❌ MCP server
- ✅ Just add the tool file!

---

## 🚀 Benefits

1. **Zero Touch Agent Updates** - Add tools, agents get them automatically
2. **Hot Reload** - Add/update tools without restarting
3. **Clean Separation** - Agents = prompts, Tools = plugins
4. **Easy Testing** - Test tools independently
5. **Discoverability** - List all tools: `registry.list_all_tools()`
6. **Flexible Filtering** - Domain, tags, custom filters
7. **MCP Compatibility** - Auto-expose via MCP server

---

## 📝 Implementation Checklist

### Phase 1: Core Infrastructure ✅
- [ ] Create `tools/_decorators.py` with `@tool` decorator
- [ ] Create `tools/_loader.py` with discovery engine
- [ ] Create `tools/_registry.py` with registry singleton
- [ ] Create `tools/__init__.py` that auto-runs discovery

### Phase 2: Tool Migration ⏳
- [ ] Create `tools/weather/` folder structure
- [ ] Convert `get_weather` to decorated format
- [ ] Convert `get_forecast` to decorated format
- [ ] Create `tools/stock/` folder structure
- [ ] Convert `get_stock_price` to decorated format
- [ ] Convert `get_stock_analysis` to decorated format
- [ ] Convert `get_stock_history` to decorated format
- [ ] Test auto-discovery

### Phase 3: Agent Factory ⏳
- [ ] Create YAML config schema
- [ ] Implement `agent_factory.py`
- [ ] Create `agents/weather_agent.yaml`
- [ ] Create `agents/stock_agent.yaml`
- [ ] Test dynamic agent creation

### Phase 4: MCP Server ⏳
- [ ] Implement dynamic MCP server
- [ ] Add hot-reload capability
- [ ] Create server configuration
- [ ] Test with MCP clients

### Phase 5: Documentation ⏳
- [ ] Write tool creation guide
- [ ] Document decorator API
- [ ] Create example tools
- [ ] Update README

---

## 🔧 Testing Strategy

### Unit Tests
```python
def test_tool_decorator():
    @tool(domain="test", tags=["example"])
    def example_tool():
        return "test"

    assert hasattr(example_tool, '_tool_metadata')
    assert example_tool._tool_metadata['domain'] == "test"

def test_tool_discovery():
    loader = ToolLoader()
    tools = loader.discover_tools()
    assert len(tools) > 0
    assert "weather.get_weather" in tools

def test_registry():
    registry = ToolRegistry()
    weather_tools = registry.get_tools_by_domain("weather")
    assert len(weather_tools) > 0
```

---

## 📚 API Reference

### @tool Decorator
```python
@tool(
    domain: str,              # Required: tool domain
    name: str = None,         # Optional: override function name
    description: str = None,  # Optional: override docstring
    tags: list[str] = None,   # Optional: searchable tags
    mock: bool = False,       # Optional: mock implementation flag
    requires_api_key: str = None  # Optional: required env var
)
```

### ToolRegistry Methods
- `register_tool(tool_id, func, metadata)` - Register a tool
- `get_tools_by_domain(domain)` - Get all tools for domain
- `get_tools_by_tags(tags)` - Get tools by tags
- `get_tool(tool_id)` - Get specific tool
- `list_all_tools()` - Get all tools
- `list_domains()` - List available domains

### AgentFactory Methods
- `from_yaml(config_path)` - Create agent from YAML
- `list_available_configs(dir)` - List agent configs

---

## 🎯 Success Criteria

- ✅ Add new tool file → Agent automatically discovers it
- ✅ No agent code changes when adding tools
- ✅ MCP server auto-exposes new tools
- ✅ Hot-reload capability working
- ✅ Tool filtering by domain and tags
- ✅ Clean separation of concerns
- ✅ Comprehensive documentation

---

**Last Updated**: October 24, 2025
**Status**: Implementation in Progress
**Next Phase**: Phase 1 - Core Infrastructure
