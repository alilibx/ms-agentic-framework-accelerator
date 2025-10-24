# Agentic Multi-Agent System

A dynamic, plugin-based multi-agent system built on Microsoft's Agent Framework with automatic tool and agent discovery. Create powerful AI agents with just YAML configuration files - no code required!

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### Dynamic Tool Discovery
- **Zero-Code Tool Integration**: Drop a Python file in `tools/domain/` and it's automatically available
- **Decorator-Based Registration**: Simple `@tool` decorator handles all registration
- **Domain Organization**: Tools organized by business domain (weather, stock, email, calendar)
- **Tag-Based Filtering**: Fine-grained control over which tools each agent gets
- **Hot-Reload Support**: Modify tools without restarting the system

### Automatic Agent Discovery
- **YAML-Based Configuration**: Define agents declaratively without writing Python
- **Zero-Code Agent Creation**: Drop a YAML file in `agents/` and it's immediately available
- **Automatic Tool Attachment**: Agents automatically discover and attach tools based on domains/tags
- **No Manual Registration**: No need to edit `__init__.py` or import statements

### Microsoft Agent Framework Integration
- **Sequential Workflows**: Chain agents in sequence for complex workflows
- **Parallel Execution**: Run multiple agents concurrently with fan-out/fan-in patterns
- **Custom Aggregators**: Combine parallel results with custom logic
- **Azure OpenAI Support**: Production-ready integration with Azure services

### Developer Experience
- **DevUI Integration**: Built-in web interface for testing and debugging
- **Comprehensive Logging**: Detailed logs for tool discovery and agent creation
- **Mock & Real APIs**: Easy toggle between mock data and real API integrations
- **Type Safety**: Full type hints and annotations throughout

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Project Structure](#-project-structure)
- [Core Concepts](#-core-concepts)
- [Creating Tools](#-creating-tools)
- [Creating Agents](#-creating-agents)
- [Running the System](#-running-the-system)
- [Examples](#-examples)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Azure OpenAI access (or modify for OpenAI/other providers)
- Azure CLI installed and authenticated

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/agentic-ms.git
cd agentic-ms
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Azure credentials**
```bash
# Login to Azure CLI
az login

# Set your subscription (if needed)
az account set --subscription "your-subscription-id"
```

5. **Update agent configurations**

Edit the `model` section in agent YAML files (`agents/*.yaml`) with your Azure OpenAI endpoint:

```yaml
model:
  endpoint: "https://your-azure-openai.openai.azure.com/"
  deployment: "your-deployment-name"
  credential_type: "azure_cli"
```

6. **Run the DevUI**
```bash
python run_devui.py
```

Open http://localhost:8080 in your browser and start chatting with agents!

## 📁 Project Structure

```
agentic-ms/
├── agents/                      # Agent YAML configurations
│   ├── agent_factory.py        # Factory for creating agents from YAML
│   ├── __init__.py             # Auto-discovery of all agents
│   ├── weather_agent.yaml      # Weather assistant configuration
│   ├── stock_agent.yaml        # Stock market assistant configuration
│   ├── email_agent.yaml        # Email assistant configuration
│   └── calendar_agent.yaml     # Calendar assistant configuration
│
├── tools/                       # Tool library (auto-discovered)
│   ├── _decorators.py          # @tool decorator for registration
│   ├── _registry.py            # Central tool registry (singleton)
│   ├── _loader.py              # Auto-discovery engine
│   ├── __init__.py             # Package initialization
│   │
│   ├── weather/                # Weather domain tools
│   │   ├── current_weather.py
│   │   └── forecast.py
│   │
│   ├── stock/                  # Stock market domain tools
│   │   ├── stock_price.py
│   │   ├── stock_analysis.py
│   │   └── stock_history.py
│   │
│   ├── email/                  # Email domain tools
│   │   ├── send_email.py
│   │   ├── read_inbox.py
│   │   └── search_emails.py
│   │
│   ├── calendar/               # Calendar domain tools
│   │   ├── create_event.py
│   │   ├── list_events.py
│   │   └── find_free_time.py
│   │
│   └── common/                 # Shared utility tools
│
├── workflows/                   # Workflow orchestrations
│   ├── financial_workflow.py  # Sequential workflow example
│   └── reusable_workflows.py  # Parallel workflow examples
│
├── docs/                        # Documentation
│   ├── DYNAMIC_TOOL_ARCHITECTURE.md
│   ├── AGENT_WORKFLOW_ARCHITECTURE.md
│   ├── PARALLEL_EXECUTION_QUICKSTART.md
│   └── EMAIL_AGENT_DEMO.md
│
├── demos/                       # Demo scripts
│   ├── demo_parallel_execution.py
│   └── workflow_runner.py
│
├── run_devui.py                # Launch DevUI with all agents
├── test_agent_factory.py       # Test YAML-based agents
├── test_auto_discovery.py      # Test automatic discovery
└── requirements.txt            # Python dependencies
```

## 💡 Core Concepts

### 1. Tools

Tools are Python functions decorated with `@tool` that provide specific capabilities to agents.

**Key Features:**
- Automatic discovery via filesystem scanning
- Domain-based organization (weather, stock, email, etc.)
- Tag-based filtering for fine-grained control
- Mock vs real API support

### 2. Agents

Agents are AI assistants configured via YAML files that automatically discover and use tools.

**Key Features:**
- Declarative YAML configuration
- Automatic tool attachment based on domains/tags
- Editable prompts without code changes
- Azure OpenAI integration

### 3. Workflows

Workflows orchestrate multiple agents to solve complex tasks.

**Types:**
- **Sequential**: Agents run one after another
- **Parallel**: Agents run concurrently (fan-out/fan-in)
- **Custom**: Build complex routing and conditional logic

## 🛠 Creating Tools

### Step 1: Create a Tool File

Create a Python file in the appropriate domain folder:

```python
# tools/weather/humidity.py
from typing import Annotated
from tools._decorators import tool

@tool(
    domain="weather",
    description="Get humidity levels for a location",
    tags=["weather", "humidity", "conditions"],
    mock=True,  # Set to False when using real APIs
)
def get_humidity(
    location: Annotated[str, "The location to check humidity for"]
) -> str:
    """Get humidity percentage for a given location.

    Args:
        location: City name or location string

    Returns:
        Formatted string with humidity information
    """
    # Mock implementation
    return f"Humidity in {location}: 65%"
```

### Step 2: That's It!

The tool is now:
- ✅ Automatically discovered at startup
- ✅ Registered in the tool registry
- ✅ Available to all agents with `tool_domains: ["weather"]`

**No code editing, imports, or registration needed!**

### Tool Decorator Parameters

```python
@tool(
    domain: str,              # Required: Tool domain (weather, stock, email, etc.)
    name: Optional[str],      # Optional: Tool name (defaults to function name)
    description: Optional[str], # Optional: Description (defaults to docstring)
    tags: Optional[list],     # Optional: Additional tags for filtering
    mock: bool = False,       # Optional: Is this a mock implementation?
    requires_api_key: Optional[str], # Optional: API key environment variable
)
```

## 🤖 Creating Agents

### Step 1: Create a YAML Configuration

Create a YAML file in the `agents/` directory:

```yaml
# agents/news_agent.yaml
name: "News Assistant"
description: "Provides latest news headlines and articles"

# Tool Discovery - automatically finds matching tools
tool_domains:
  - news

tool_tags:
  - news
  - headlines
  - articles

# Optional: Exclude specific tools
# exclude_tools:
#   - news.experimental_feature

# Agent Instructions (the "prompt")
instructions: |
  You are a news assistant. Provide latest news headlines
  and articles when asked. Always cite your sources and
  present information objectively.

  When users ask about news:
  1. Use the appropriate tool to fetch articles
  2. Summarize key points clearly
  3. Provide source attribution

# Model Configuration
model:
  endpoint: "https://your-azure-openai.openai.azure.com/"
  deployment: "gpt-4o"
  credential_type: "azure_cli"
```

### Step 2: Create Domain Tools (if needed)

If the domain doesn't exist, create tools for it:

```python
# tools/news/get_headlines.py
from tools._decorators import tool

@tool(domain="news", description="Get latest news headlines")
def get_headlines(category: str = "general") -> str:
    """Fetch latest news headlines."""
    # Implementation here
    return "Latest headlines..."
```

### Step 3: Restart and Use!

```bash
python run_devui.py
```

The news agent is now automatically:
- ✅ Discovered from the YAML file
- ✅ Created with matching tools attached
- ✅ Available in the DevUI

**No Python code editing required!**

## 🏃 Running the System

### DevUI (Web Interface)

Launch the development web interface:

```bash
python run_devui.py
```

Features:
- Chat with individual agents
- Test workflows
- View agent capabilities
- Debug tool calls

### Python API

Use agents programmatically:

```python
from agents import get_all_agents
import asyncio

async def main():
    # Get all auto-discovered agents
    agents = get_all_agents()

    # Use weather agent
    weather_agent = agents['weather_agent']
    response = await weather_agent.run("What's the weather in Tokyo?")
    print(response)

asyncio.run(main())
```

### Testing

Run the test suites:

```bash
# Test tool discovery
python -c "from tools import ToolRegistry; print(ToolRegistry().get_summary())"

# Test agent creation
python test_agent_factory.py

# Test automatic discovery
python test_auto_discovery.py
```

## 📚 Examples

### Example 1: Simple Agent Query

```python
from agents import get_all_agents
import asyncio

async def main():
    agents = get_all_agents()
    weather_agent = agents['weather_agent']

    response = await weather_agent.run(
        "What's the weather forecast for Seattle this week?"
    )
    print(response)

asyncio.run(main())
```

### Example 2: Sequential Workflow

```python
from agent_framework import SequentialBuilder
from agents import get_all_agents

agents = get_all_agents()
stock_agent = agents['stock_agent']
weather_agent = agents['weather_agent']

workflow = (
    SequentialBuilder()
    .add_agent(stock_agent)
    .add_agent(weather_agent)
    .build()
)

# Execute: stock analysis → weather check
result = await workflow.run("Analyze AAPL and check weather in Cupertino")
```

### Example 3: Parallel Workflow

```python
from agent_framework import ConcurrentBuilder
from agents import get_all_agents

agents = get_all_agents()

workflow = (
    ConcurrentBuilder()
    .participants([agents['stock_agent'], agents['weather_agent']])
    .build()
)

# Both agents run simultaneously
result = await workflow.run("Get AAPL price and Seattle weather")
```

### Example 4: Creating a Custom Tool

```python
# tools/news/search_articles.py
from typing import Annotated
from tools._decorators import tool

@tool(
    domain="news",
    description="Search news articles by keyword",
    tags=["news", "search", "articles"],
    mock=True
)
def search_articles(
    query: Annotated[str, "Search query"],
    days: Annotated[int, "Days to look back"] = 7
) -> str:
    """Search for news articles matching the query."""
    return f"Found 10 articles about '{query}' from last {days} days"
```

## 🏗 Architecture

### Dynamic Tool Discovery Flow

```
1. Application Startup
   ↓
2. ToolLoader scans tools/ directory
   ↓
3. Finds all files with @tool decorator
   ↓
4. Registers tools in ToolRegistry (singleton)
   ↓
5. Tools available to all agents
```

### Agent Creation Flow

```
1. Application Startup
   ↓
2. AgentFactory scans agents/ directory
   ↓
3. Finds all *.yaml files
   ↓
4. For each YAML:
   a. Parse configuration
   b. Query ToolRegistry for matching tools
   c. Create ChatAgent with tools
   ↓
5. Agents exported via agents/__init__.py
   ↓
6. Agents available in DevUI and Python API
```

### Tool Registry (Singleton)

The ToolRegistry maintains a central registry of all discovered tools:

- **Domain Filtering**: Get all tools for a specific domain
- **Tag Filtering**: Get tools matching specific tags
- **Metadata Storage**: Store tool descriptions, parameters, etc.
- **Hot-Reload**: Refresh tools without restarting

## ⚙️ Configuration

### Agent Configuration (YAML)

```yaml
name: "Agent Name"                    # Required: Display name
description: "Agent description"      # Required: Short description

tool_domains:                         # Optional: Domain filters
  - domain1
  - domain2

tool_tags:                            # Optional: Tag filters
  - tag1
  - tag2

exclude_tools:                        # Optional: Tools to exclude
  - tool.name

instructions: |                       # Required: Agent prompt
  Your instructions here...

model:                                # Required: Model config
  endpoint: "https://..."             # Azure OpenAI endpoint
  deployment: "model-name"            # Deployment name
  credential_type: "azure_cli"        # Credential type
```

### Environment Variables

Create a `.env` file for API keys:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Optional: Real API keys for tools
OPENWEATHER_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

### Tool Configuration

```python
@tool(
    domain="your_domain",           # Required
    name="tool_name",               # Optional
    description="What it does",    # Optional
    tags=["tag1", "tag2"],         # Optional
    mock=True,                     # Use mock data (True/False)
    requires_api_key="API_KEY_ENV" # Environment variable name
)
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Create a branch: `git checkout -b feature/your-feature`

### Adding a New Domain

1. **Create domain folder**: `mkdir tools/your_domain`
2. **Add `__init__.py`**: `touch tools/your_domain/__init__.py`
3. **Create tools**: Add Python files with `@tool` decorators
4. **Create agent YAML**: Add `agents/your_domain_agent.yaml`
5. **Test**: Run `python test_auto_discovery.py`
6. **Submit PR**: Create a pull request with your changes

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings to all public functions
- Use meaningful variable names
- Keep functions focused and small

### Testing

Before submitting a PR:

```bash
# Test tool discovery
python -c "from tools import ToolRegistry; ToolRegistry().get_summary()"

# Test agent creation
python test_agent_factory.py

# Test your new domain
python test_auto_discovery.py
```

### Pull Request Process

1. Update documentation for new features
2. Add examples if adding new capabilities
3. Ensure all tests pass
4. Update README if needed
5. Describe changes in PR description

## 📖 Documentation

Comprehensive documentation available in the `docs/` folder:

- **[Dynamic Tool Architecture](docs/DYNAMIC_TOOL_ARCHITECTURE.md)**: Complete guide to the tool system
- **[Agent Workflow Architecture](docs/AGENT_WORKFLOW_ARCHITECTURE.md)**: Sequential and parallel workflows
- **[Parallel Execution Quickstart](docs/PARALLEL_EXECUTION_QUICKSTART.md)**: Quick guide to parallel patterns
- **[Email Agent Demo](docs/EMAIL_AGENT_DEMO.md)**: Step-by-step example of creating an agent

## 🐛 Troubleshooting

### Tools Not Discovered

**Problem**: Tools not showing up in registry

**Solution**:
1. Check file is in `tools/domain/` directory
2. Ensure `@tool` decorator is present
3. Verify `__init__.py` exists in domain folder
4. Check logs for import errors

### Agent Not Created

**Problem**: Agent YAML file not creating agent

**Solution**:
1. Verify YAML syntax is correct
2. Check domain names match tool domains
3. Ensure Azure OpenAI credentials are configured
4. Check logs for errors during discovery

### Connection Errors

**Problem**: Azure OpenAI connection fails

**Solution**:
1. Verify endpoint URL is correct (must include `.azure.com`)
2. Check Azure CLI is authenticated: `az account show`
3. Verify deployment name matches your Azure setup
4. Check network connectivity

## 🤖 Available Agents

The system includes 4 pre-built agents with 11 tools across 4 domains:

### 🌤️ Weather Assistant
- **Tools**: 2 (current weather, forecast)
- **Use Cases**: Weather forecasts, current conditions
- **Example**: "What's the weather in Tokyo?"

### 📈 Stock Market Assistant
- **Tools**: 3 (price, analysis, history)
- **Use Cases**: Stock prices, analyst ratings, historical data
- **Example**: "Analyze AAPL stock"

### 📧 Email Assistant
- **Tools**: 3 (send, read inbox, search)
- **Use Cases**: Email management, inbox checking
- **Example**: "Show me my unread emails"

### 📅 Calendar Assistant
- **Tools**: 3 (create event, list events, find free time)
- **Use Cases**: Schedule management, availability checking
- **Example**: "Find me a free slot tomorrow afternoon"

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft Agent Framework**: Core agent orchestration framework
- **Azure OpenAI**: LLM infrastructure
- **Contributors**: Thanks to all contributors who help improve this project

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/agentic-ms/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/agentic-ms/discussions)

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Dynamic tool discovery
- ✅ Automatic agent discovery
- ✅ YAML-based configuration
- ✅ Sequential workflows
- ✅ Parallel workflows
- ✅ DevUI integration

### Planned Features (v2.0)
- 🔄 MCP Server implementation
- 🔄 Real API integrations (OpenWeatherMap, Alpha Vantage)
- 🔄 Tool versioning system
- 🔄 Agent performance monitoring
- 🔄 Hot-reload without restart
- 🔄 Plugin marketplace

### Future Enhancements
- Multiple LLM provider support (OpenAI, Anthropic, etc.)
- Tool dependency management
- Conditional workflow routing
- Agent-to-agent communication
- Distributed agent execution
- Web-based agent configuration UI

---

**Made with ❤️ using Microsoft Agent Framework**

*Star ⭐ this repo if you find it useful!*
