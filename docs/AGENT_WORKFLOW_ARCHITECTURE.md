# Agent and Workflow Architecture Guide

## Overview

This document explains how standalone agents (`weather_agent.py`, `stock_agent.py`) relate to workflows (`agentic_azure.py`) and demonstrates how to reuse agents across workflows instead of defining them inline.

---

## Current Architecture

### Standalone Agents (Reusable Components)

**weather_agent.py**
- **Agent Name:** "My Custom Weather Agent"
- **Tools:** `get_weather()`, `get_forecast()`
- **Purpose:** Provides weather information and forecasts
- **Usage:** Can be used independently via DevUI or programmatically

**stock_agent.py**
- **Agent Name:** "My Stock Agent"
- **Tools:** `get_stock_price()`, `get_stock_analysis()`, `get_stock_history()`
- **Purpose:** Provides stock market data and analysis
- **Usage:** Can be used independently via DevUI or programmatically

### Workflow-Specific Agents (Defined Inline)

**agentic_azure.py** defines three agents directly:

1. **Market Analyzer**
   - Tools: `analyze_market_conditions()`, `get_sector_performance()`
   - Purpose: Analyzes market conditions

2. **Weather Analyst**
   - Tools: `get_weather_impact()`
   - Purpose: Analyzes weather impact on markets
   - **Note:** Different from `weather_agent` - has different tools and purpose

3. **Investment Advisor**
   - Tools: `generate_investment_recommendation()`
   - Purpose: Provides investment recommendations

### Current Workflow Structure

```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(market_analyzer)      # Inline agent
    .add_edge(market_analyzer, weather_analyst) # Inline agent
    .add_edge(weather_analyst, investment_advisor) # Inline agent
    .build()
)
```

**Flow:** Market Analyzer → Weather Analyst → Investment Advisor

---

## Can Standalone Agents Be Used in Workflows?

**YES!** Standalone agents can absolutely be used in workflows. All agents are `ChatAgent` instances, making them fully compatible with `WorkflowBuilder`.

### Benefits of Using Standalone Agents in Workflows:

1. **Reusability:** Define agents once, use them in multiple workflows
2. **Modularity:** Separate agent definitions from workflow logic
3. **Maintainability:** Update agent behavior in one place
4. **Testing:** Test agents independently before integrating into workflows
5. **Composition:** Mix and match agents to create different workflows

---

## How to Use Standalone Agents in Workflows

### Option 1: Import and Use Directly

**Example: Create a workflow using existing standalone agents**

```python
# File: stock_weather_workflow.py
from weather_agent import weather_agent
from stock_agent import stock_agent
from agent_framework import WorkflowBuilder

# Create a workflow using imported agents
stock_weather_workflow = (
    WorkflowBuilder()
    .set_start_executor(stock_agent)      # Use standalone stock agent
    .add_edge(stock_agent, weather_agent)  # Use standalone weather agent
    .build()
)

# Usage
result = await stock_weather_workflow.run(
    "What's the stock price for AAPL and how's the weather in Cupertino?"
)
```

**Benefits:**
- No code duplication
- Agents remain reusable
- Clean separation of concerns

### Option 2: Refactor Existing Workflow

**Before (agentic_azure.py - Current approach):**
```python
# Agents defined inline in the workflow file
market_analyzer = ChatAgent(
    name="Market Analyzer",
    # ... all configuration here ...
)

weather_analyst = ChatAgent(
    name="Weather Analyst",
    # ... all configuration here ...
)

workflow = (
    WorkflowBuilder()
    .set_start_executor(market_analyzer)
    .add_edge(market_analyzer, weather_analyst)
    .build()
)
```

**After (Recommended approach):**

```python
# File: agents/market_analyzer_agent.py
market_analyzer = ChatAgent(
    name="Market Analyzer",
    description="Analyzes market conditions and trends",
    # ... configuration ...
)
__all__ = ["market_analyzer"]

# File: agents/weather_analyst_agent.py
weather_analyst = ChatAgent(
    name="Weather Analyst",
    description="Analyzes weather impact on markets",
    # ... configuration ...
)
__all__ = ["weather_analyst"]

# File: workflows/financial_analysis_workflow.py
from agents.market_analyzer_agent import market_analyzer
from agents.weather_analyst_agent import weather_analyst
from agents.investment_advisor_agent import investment_advisor
from agent_framework import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .set_start_executor(market_analyzer)
    .add_edge(market_analyzer, weather_analyst)
    .add_edge(weather_analyst, investment_advisor)
    .build()
)
```

**Benefits:**
- Agents can be used in multiple workflows
- Each agent is independently testable
- Cleaner file structure
- Easier to maintain

---

## Practical Examples

### Example 1: Using stock_agent in a New Workflow

```python
# File: simple_stock_workflow.py
from stock_agent import stock_agent
from agent_framework import WorkflowBuilder

# Simple single-agent workflow
stock_workflow = (
    WorkflowBuilder()
    .set_start_executor(stock_agent)
    .build()
)

# Run it
async def main():
    result = await stock_workflow.run(
        "Get me the stock price and analysis for AAPL"
    )
    print(result.get_outputs())
```

### Example 2: Combining Standalone Agents

```python
# File: combined_analysis_workflow.py
from weather_agent import weather_agent
from stock_agent import stock_agent
from agent_framework import WorkflowBuilder, ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Create a new analyzer that combines insights
combined_advisor = ChatAgent(
    name="Combined Advisor",
    description="Provides recommendations based on stock and weather data",
    instructions="""
    You receive stock market data and weather information.
    Provide comprehensive investment advice considering both factors.
    """,
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
)

# Build workflow with reusable agents
workflow = (
    WorkflowBuilder()
    .set_start_executor(stock_agent)        # Reusable
    .add_edge(stock_agent, weather_agent)    # Reusable
    .add_edge(weather_agent, combined_advisor) # New agent
    .build()
)

# Usage
result = await workflow.run(
    "Analyze AAPL stock and weather conditions in California"
)
```

### Example 3: Conditional Workflows with Standalone Agents

```python
# File: conditional_workflow.py
from weather_agent import weather_agent
from stock_agent import stock_agent
from agent_framework import WorkflowBuilder, WorkflowContext

def route_based_on_query(ctx: WorkflowContext):
    """Route to different agents based on query content"""
    user_message = ctx.get_input()

    if "stock" in user_message.lower() or "price" in user_message.lower():
        return stock_agent
    elif "weather" in user_message.lower() or "forecast" in user_message.lower():
        return weather_agent
    else:
        return stock_agent  # Default

# Conditional workflow
conditional_workflow = (
    WorkflowBuilder()
    .set_start_executor(route_based_on_query)
    .build()
)
```

### Example 4: Parallel Execution with Standalone Agents

**The framework provides the `ConcurrentBuilder` API for parallel agent execution with fan-out/fan-in patterns.**

```python
# File: parallel_analysis_workflow.py
from weather_agent import weather_agent
from stock_agent import stock_agent
from agent_framework import ConcurrentBuilder

# Simple parallel execution - both agents run simultaneously
parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .build()
)

# Usage
result = await parallel_workflow.run(
    "Analyze AAPL stock and weather in California"
)
# Both agents process the query in parallel
# Results are automatically aggregated into a list
```

**With Custom Aggregator:**

```python
from agent_framework import ConcurrentBuilder, ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Create a synthesis agent to aggregate parallel results
synthesis_agent = ChatAgent(
    name="Result Synthesizer",
    description="Combines insights from multiple agents",
    instructions="Synthesize the analysis from stock and weather agents into a unified report.",
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
)

# Parallel execution with custom aggregation
parallel_with_synthesis = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .with_aggregator(synthesis_agent)  # Agent-based aggregator
    .build()
)

# Or with a callback function aggregator
def combine_results(results):
    """Custom function to combine parallel results"""
    combined = []
    for result in results:
        if result.agent_run_response.messages:
            combined.append(result.agent_run_response.messages[-1].text)
    return " | ".join(combined)

parallel_with_callback = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .with_aggregator(combine_results)  # Function-based aggregator
    .build()
)
```

**How Parallel Execution Works:**

```
Input: "Analyze AAPL and weather in CA"
   │
   ▼
┌──────────┐
│Dispatcher│ (broadcasts to all participants)
└──────────┘
   │
   ├────────────────┬────────────────┐
   ▼                ▼                ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│ Agent 1 │   │ Agent 2  │   │ Agent 3  │  (run in parallel)
└─────────┘   └──────────┘   └──────────┘
   │                ▼                │
   └────────────────┬────────────────┘
                    ▼
              ┌───────────┐
              │Aggregator │ (fan-in: collects all results)
              └───────────┘
                    │
                    ▼
            Combined Output
```

**Benefits:**
- Faster execution - agents run simultaneously
- Multiple perspectives - different agents analyze the same input
- Flexible aggregation - combine results with custom logic
- Scales with compute resources

---

## Advanced Workflow Patterns

### 1. Fan-Out/Fan-In with WorkflowBuilder

For more control over parallel execution, use `WorkflowBuilder` with fan-out edges:

```python
from agent_framework import WorkflowBuilder, ChatAgent

# Create a dispatcher and aggregator
dispatcher = ChatAgent(name="Dispatcher", ...)
aggregator = ChatAgent(name="Aggregator", ...)

# Build workflow with explicit fan-out/fan-in
workflow = (
    WorkflowBuilder()
    .set_start_executor(dispatcher)
    .add_fan_out_edges(
        source=dispatcher,
        targets=[stock_agent, weather_agent]  # Parallel execution
    )
    .add_fan_in_edges(
        sources=[stock_agent, weather_agent],
        target=aggregator  # Collects results
    )
    .build()
)
```

### 2. Conditional Parallel Execution

```python
from agent_framework import WorkflowBuilder, Case, Default

# Router that selects which agents to run in parallel
workflow = (
    WorkflowBuilder()
    .set_start_executor(router_agent)
    .add_multi_selection_edge_group(
        source=router_agent,
        targets=[stock_agent, weather_agent, market_analyzer],
        selection_func=lambda msg, ids: select_relevant_agents(msg, ids)
    )
    .add_fan_in_edges(
        sources=[stock_agent, weather_agent, market_analyzer],
        target=aggregator
    )
    .build()
)

def select_relevant_agents(message, agent_ids):
    """Dynamically select which agents should process this message"""
    selected = []
    if "stock" in message.lower():
        selected.append(agent_ids[0])  # stock_agent
    if "weather" in message.lower():
        selected.append(agent_ids[1])  # weather_agent
    # Multiple agents can be selected for parallel execution
    return selected
```

### 3. Sequential vs Parallel Comparison

```python
from agent_framework import SequentialBuilder, ConcurrentBuilder

# Sequential: agent1 → agent2 → agent3
# Each agent receives output from previous agent
sequential_workflow = (
    SequentialBuilder()
    .participants([agent1, agent2, agent3])
    .build()
)

# Parallel: all agents receive same input simultaneously
# Results are aggregated at the end
parallel_workflow = (
    ConcurrentBuilder()
    .participants([agent1, agent2, agent3])
    .build()
)
```

### 4. Hybrid Workflows (Sequential + Parallel)

```python
# Complex workflow combining sequential and parallel patterns
workflow = (
    WorkflowBuilder()
    .set_start_executor(initial_analyzer)
    # First sequential step
    .add_edge(initial_analyzer, dispatcher)
    # Parallel fan-out
    .add_fan_out_edges(
        source=dispatcher,
        targets=[stock_agent, weather_agent, market_analyzer]
    )
    # Fan-in to collect parallel results
    .add_fan_in_edges(
        sources=[stock_agent, weather_agent, market_analyzer],
        target=synthesis_agent
    )
    # Final sequential step
    .add_edge(synthesis_agent, recommendation_agent)
    .build()
)
```

**Execution Flow:**
```
initial_analyzer (sequential)
      ↓
  dispatcher
      ↓
   ┌──┴──┬──────────┐
   ▼     ▼          ▼
stock  weather   market    (parallel)
agent   agent    analyzer
   └──┬──┴──────────┘
      ↓
 synthesis_agent (fan-in)
      ↓
recommendation_agent (sequential)
```

---

## Relationship Between Agents and Workflows

### Conceptual Model

```
┌─────────────────────────────────────────────────────┐
│                  Agent Library                       │
│  (Reusable, Standalone ChatAgent instances)         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │ weather_agent   │  │  stock_agent    │          │
│  │  - get_weather  │  │  - get_price    │          │
│  │  - get_forecast │  │  - get_analysis │          │
│  └─────────────────┘  └─────────────────┘          │
│                                                      │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │ market_analyzer │  │ weather_analyst │          │
│  └─────────────────┘  └─────────────────┘          │
│                                                      │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ Import and compose
                        │
┌───────────────────────┴─────────────────────────────┐
│                   Workflows                          │
│  (Orchestrate agents using WorkflowBuilder)         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  workflow_1:  stock_agent → weather_agent           │
│  workflow_2:  market_analyzer → weather_analyst     │
│  workflow_3:  stock_agent → market_analyzer         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Key Principles

1. **Agents are building blocks**
   - Define once, use in multiple workflows
   - Each agent has specific expertise and tools

2. **Workflows orchestrate agents**
   - Define the sequence of agent execution
   - Can use standalone or inline agents
   - Control data flow between agents

3. **Flexibility**
   - Mix standalone and inline agents in the same workflow
   - Create multiple workflows from the same agent set
   - Agents can be used independently outside workflows

---

## Comparison: Current vs Recommended Architecture

### Current Approach (agentic_azure.py)

**Pros:**
- Self-contained in one file
- Easy to understand for simple workflows
- No import dependencies

**Cons:**
- Agents cannot be reused in other workflows
- Harder to test agents independently
- Code duplication if similar agents needed elsewhere
- File becomes large with multiple agents

### Recommended Approach (Separate Agent Files)

**Pros:**
- Agents are reusable across workflows
- Each agent is independently testable
- Better code organization
- Easier to maintain and extend
- Supports composition of complex workflows

**Cons:**
- More files to manage
- Need to understand import structure
- Slightly more setup required

---

## Best Practices

### 1. Agent Organization

```
project/
├── agents/                    # Reusable agent definitions
│   ├── __init__.py
│   ├── weather_agent.py
│   ├── stock_agent.py
│   ├── market_analyzer_agent.py
│   └── investment_advisor_agent.py
├── workflows/                 # Workflow compositions
│   ├── __init__.py
│   ├── financial_analysis_workflow.py
│   ├── stock_weather_workflow.py
│   └── quick_market_workflow.py
└── run_devui.py              # DevUI entry point
```

### 2. Agent Definition Template

```python
# agents/example_agent.py
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from typing import Annotated

# Define tools
def example_tool(
    param: Annotated[str, "Description of parameter"]
) -> str:
    """Tool description."""
    # Implementation
    return result

# Create agent instance
example_agent = ChatAgent(
    name="Example Agent",
    description="Brief description for DevUI",
    instructions="""
    Detailed instructions for the agent's behavior.
    """,
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
    tools=[example_tool],
)

# Export
__all__ = ["example_agent"]
```

### 3. Workflow Definition Template

```python
# workflows/example_workflow.py
from agents.agent_a import agent_a
from agents.agent_b import agent_b
from agent_framework import WorkflowBuilder

# Build workflow
example_workflow = (
    WorkflowBuilder()
    .set_start_executor(agent_a)
    .add_edge(agent_a, agent_b)
    .build()
)

# Export
__all__ = ["example_workflow"]
```

### 4. DevUI Registration

```python
# run_devui.py
from agent_framework.dev_ui import serve

# Import standalone agents
from weather_agent import weather_agent
from stock_agent import stock_agent

# Import workflows
from workflows.financial_analysis_workflow import workflow as fin_workflow
from workflows.stock_weather_workflow import stock_weather_workflow

# Register all entities
serve(
    entities=[
        weather_agent,
        stock_agent,
        fin_workflow,
        stock_weather_workflow,
    ],
    port=8080,
    auto_open=True
)
```

---

## Migration Guide

### Migrating agentic_azure.py to Use Standalone Agents

If you want to refactor your current workflow to use reusable agents:

**Step 1: Create agent files**
```bash
mkdir -p agents
```

**Step 2: Extract each agent to its own file**
```python
# agents/market_analyzer_agent.py
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Copy tool functions
def analyze_market_conditions() -> str:
    # ... existing implementation ...
    pass

def get_sector_performance() -> str:
    # ... existing implementation ...
    pass

# Copy agent definition
market_analyzer = ChatAgent(
    name="Market Analyzer",
    # ... rest of config ...
    tools=[analyze_market_conditions, get_sector_performance]
)

__all__ = ["market_analyzer"]
```

**Step 3: Update workflow file**
```python
# workflows/financial_analysis_workflow.py
from agents.market_analyzer_agent import market_analyzer
from agents.weather_analyst_agent import weather_analyst
from agents.investment_advisor_agent import investment_advisor
from agent_framework import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .set_start_executor(market_analyzer)
    .add_edge(market_analyzer, weather_analyst)
    .add_edge(weather_analyst, investment_advisor)
    .build()
)

__all__ = ["workflow"]
```

**Step 4: Update imports in other files**
```python
# agentic_azure.py or run_devui.py
from workflows.financial_analysis_workflow import workflow
```

---

## Inputs for Different Scenarios

### Standalone Agents (Direct Usage)

```python
# weather_agent.py - Direct usage
from weather_agent import weather_agent

result = await weather_agent.run("What's the weather in San Francisco?")
# Input: Natural language string
# Output: Weather information
```

### Workflows Using Standalone Agents

```python
# Using weather_agent in a workflow
from weather_agent import weather_agent
from stock_agent import stock_agent
from agent_framework import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .set_start_executor(stock_agent)
    .add_edge(stock_agent, weather_agent)
    .build()
)

result = await workflow.run(
    "Get AAPL stock price and weather in Cupertino"
)
# Input: Natural language combining both agent contexts
# Output: Combined analysis from both agents
```

### Current Inline Workflow

```python
# agentic_azure.py - Current approach
from agentic_azure import workflow

result = await workflow.run(
    "Analyze current market conditions and provide investment advice"
)
# Input: Natural language query
# Output: Market analysis → Weather impact → Investment recommendations
```

---

## Summary

### Agent Comparison

| Aspect | Standalone Agents | Inline Workflow Agents |
|--------|------------------|----------------------|
| **Reusability** | High - use in multiple workflows | Low - tied to one workflow |
| **Testability** | Easy - test independently | Harder - need workflow context |
| **Maintainability** | Good - single source of truth | Poor - duplicate code |
| **Use Case** | General-purpose agents | Workflow-specific logic |
| **Example** | `weather_agent.py`, `stock_agent.py` | Agents in `agentic_azure.py` |

### Workflow Execution Patterns

| Pattern | API | Execution | Use Case | Performance |
|---------|-----|-----------|----------|-------------|
| **Sequential** | `WorkflowBuilder` + `add_edge` | One agent at a time | Pipeline, chain of reasoning | Slower but ordered |
| **Parallel** | `ConcurrentBuilder` | All agents simultaneously | Multiple perspectives | Faster, scales with compute |
| **Conditional** | `add_switch_case_edge_group` | Route to one agent | Decision-based routing | Efficient single path |
| **Multi-selection** | `add_multi_selection_edge_group` | Route to subset | Selective parallel execution | Flexible parallelism |
| **Fan-out/Fan-in** | `add_fan_out_edges` + `add_fan_in_edges` | Broadcast → collect | Distributed analysis | Custom parallel control |
| **Hybrid** | Mix of above | Sequential + parallel | Complex workflows | Optimized execution |

### Parallel Execution Quick Reference

```python
# CONCURRENT: Run agents in parallel (fastest)
from agent_framework import ConcurrentBuilder
workflow = ConcurrentBuilder().participants([agent1, agent2]).build()

# SEQUENTIAL: Run agents one after another (ordered)
from agent_framework import SequentialBuilder
workflow = SequentialBuilder().participants([agent1, agent2]).build()

# CUSTOM: Fine-grained control over execution
from agent_framework import WorkflowBuilder
workflow = (
    WorkflowBuilder()
    .set_start_executor(agent1)
    .add_fan_out_edges(agent1, [agent2, agent3])  # Parallel
    .add_fan_in_edges([agent2, agent3], agent4)    # Synchronize
    .build()
)
```

**Recommendation:**
- Use **standalone agents** for reusable, general-purpose functionality
- Define agents **inline in workflows** only when they're highly workflow-specific
- Use **ConcurrentBuilder** for parallel execution when speed and multiple perspectives are needed
- Use **SequentialBuilder** when output from one agent feeds into the next
- Use **WorkflowBuilder** for complex hybrid patterns mixing sequential and parallel execution
- The current `weather_agent.py` and `stock_agent.py` are perfect examples of reusable agents
- Consider refactoring `agentic_azure.py` to use separate agent files for better maintainability

**Answer to Your Question:**
> "Can these agents be used in the workflow rather than specifying the agents in the agentic_azure.py file?"

**YES!** You can absolutely import and use `weather_agent` and `stock_agent` directly in workflows. They're fully compatible with:
- `WorkflowBuilder` (for sequential or custom patterns)
- `ConcurrentBuilder` (for parallel execution)
- `SequentialBuilder` (for pipeline patterns)

These standalone agents can replace or complement the inline agents in `agentic_azure.py`, and can be combined in multiple workflow patterns including parallel execution for faster results.
