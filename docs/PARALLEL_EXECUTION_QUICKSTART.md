# Parallel Execution Quick Start Guide

## TL;DR - Parallel Agent Execution

**YES, Microsoft Agent Framework supports parallel execution!** Use `ConcurrentBuilder` to run multiple agents simultaneously.

```python
from agent_framework import ConcurrentBuilder
from weather_agent import weather_agent
from stock_agent import stock_agent

# Run both agents in parallel
parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .build()
)

result = await parallel_workflow.run("Analyze AAPL and weather in CA")
```

---

## When to Use Parallel Execution

| Scenario | Use This | Why |
|----------|----------|-----|
| Need multiple perspectives on same input | `ConcurrentBuilder` | Faster, gets diverse analysis |
| Each agent needs previous agent's output | `SequentialBuilder` | Output flows through pipeline |
| Complex routing and branching | `WorkflowBuilder` | Full control over execution |
| Conditional execution based on input | `add_switch_case_edge_group` | Route to relevant agents |

---

## Three Ways to Build Workflows

### 1. ConcurrentBuilder (Parallel Execution)

**Best for:** Getting multiple perspectives simultaneously

```python
from agent_framework import ConcurrentBuilder

# All agents receive the same input and run simultaneously
workflow = ConcurrentBuilder().participants([agent1, agent2, agent3]).build()
```

**Execution:**
```
Input → [Agent1, Agent2, Agent3] (parallel) → Aggregated Results
```

### 2. SequentialBuilder (Pipeline Execution)

**Best for:** Chain of reasoning where each step builds on previous

```python
from agent_framework import SequentialBuilder

# Output from agent1 → agent2 → agent3
workflow = SequentialBuilder().participants([agent1, agent2, agent3]).build()
```

**Execution:**
```
Input → Agent1 → Agent2 → Agent3 → Final Result
```

### 3. WorkflowBuilder (Custom Execution)

**Best for:** Complex patterns with branching, fan-out/fan-in, conditionals

```python
from agent_framework import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .set_start_executor(agent1)
    .add_fan_out_edges(agent1, [agent2, agent3])  # Parallel
    .add_fan_in_edges([agent2, agent3], agent4)    # Collect
    .build()
)
```

**Execution:**
```
Input → Agent1 → [Agent2, Agent3] (parallel) → Agent4 → Result
```

---

## Complete Examples

### Example 1: Simple Parallel Analysis

```python
from weather_agent import weather_agent
from stock_agent import stock_agent
from agent_framework import ConcurrentBuilder

parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .build()
)

# Both agents analyze simultaneously
result = await parallel_workflow.run(
    "How will weather affect AAPL stock?"
)
```

### Example 2: Parallel with Custom Aggregator (Function)

```python
def combine_results(results):
    """Combine outputs from parallel agents"""
    combined = []
    for result in results:
        if result.agent_run_response.messages:
            text = result.agent_run_response.messages[-1].text
            combined.append(text)
    return " | ".join(combined)

parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .with_aggregator(combine_results)
    .build()
)
```

### Example 3: Parallel with Synthesis Agent (Agent Aggregator)

```python
from agent_framework import ChatAgent, ConcurrentBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

synthesis_agent = ChatAgent(
    name="Synthesizer",
    description="Combines insights from multiple agents",
    instructions="Synthesize the analysis into a unified recommendation.",
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
)

parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .with_aggregator(synthesis_agent)  # AI-powered aggregation
    .build()
)
```

### Example 4: Hybrid Sequential + Parallel

```python
# Complex workflow: sequential start, parallel middle, sequential end
hybrid_workflow = (
    WorkflowBuilder()
    .set_start_executor(analyzer)           # Sequential
    .add_fan_out_edges(                     # Parallel fan-out
        analyzer,
        [stock_agent, weather_agent, news_agent]
    )
    .add_fan_in_edges(                      # Collect results
        [stock_agent, weather_agent, news_agent],
        synthesizer
    )
    .add_edge(synthesizer, recommender)     # Sequential
    .build()
)
```

**Execution:**
```
analyzer (sequential)
    ↓
┌───┼───┬────┐
↓   ↓   ↓    ↓
stock weather news  (parallel)
└───┼───┴────┘
    ↓
synthesizer (fan-in)
    ↓
recommender (sequential)
```

---

## Performance Comparison

| Pattern | Agents: 3 | Time (approx) | Use Case |
|---------|-----------|---------------|----------|
| **Sequential** | A→B→C | 3x | Each needs previous output |
| **Parallel** | [A,B,C] | 1x | All analyze same input |
| **Hybrid** | A→[B,C]→D | 2x | Best of both |

*Note: Parallel execution scales with available compute resources*

---

## Key APIs Reference

### ConcurrentBuilder

```python
ConcurrentBuilder()
    .participants([agent1, agent2, ...])
    .with_aggregator(func_or_agent)  # Optional
    .with_checkpointing(storage)      # Optional
    .build()
```

### WorkflowBuilder Edge Types

```python
# Sequential edge
.add_edge(source, target)

# Parallel fan-out (broadcast to all)
.add_fan_out_edges(source, [target1, target2, ...])

# Synchronization fan-in (wait for all sources)
.add_fan_in_edges([source1, source2, ...], target)

# Conditional routing (one destination)
.add_switch_case_edge_group(source, [
    Case(condition=lambda msg: ..., target=agent1),
    Default(target=fallback)
])

# Multi-selection (route to subset)
.add_multi_selection_edge_group(
    source,
    targets=[agent1, agent2, agent3],
    selection_func=lambda msg, ids: [ids[0], ids[2]]
)
```

---

## Running Your Parallel Workflows

### Via Python Script

```python
import asyncio
from example_reusable_workflow import parallel_workflow

async def main():
    result = await parallel_workflow.run("Your query here")
    print(result.get_outputs())

asyncio.run(main())
```

### Via DevUI (Web Interface)

```python
# In run_devui.py
from agent_framework.dev_ui import serve
from example_reusable_workflow import parallel_workflow

serve(
    entities=[
        parallel_workflow,
        # ... other agents/workflows
    ],
    port=8080,
    auto_open=True
)
```

Then run:
```bash
python run_devui.py
# Opens browser at http://localhost:8080
```

---

## Files in This Project

| File | Purpose |
|------|---------|
| `AGENT_WORKFLOW_ARCHITECTURE.md` | Comprehensive guide on agent reusability and workflow patterns |
| `example_reusable_workflow.py` | Working code examples of sequential, parallel, and hybrid workflows |
| `PARALLEL_EXECUTION_QUICKSTART.md` | This file - quick reference for parallel execution |
| `weather_agent.py` | Standalone weather agent (reusable) |
| `stock_agent.py` | Standalone stock analysis agent (reusable) |
| `agentic_azure.py` | Sequential workflow with inline agents (current approach) |

---

## Next Steps

1. **Read the full guide:** See `AGENT_WORKFLOW_ARCHITECTURE.md` for detailed explanations
2. **Try the examples:** Run code from `example_reusable_workflow.py`
3. **Experiment with patterns:** Mix sequential and parallel execution
4. **Refactor existing code:** Convert inline agents to standalone agents
5. **Build your own:** Create workflows combining your existing agents

---

## Common Patterns

### Pattern 1: Multi-Agent Analysis (Parallel)
```python
# Get diverse perspectives on the same question
ConcurrentBuilder().participants([expert1, expert2, expert3])
```

### Pattern 2: Sequential Pipeline
```python
# Research → Analyze → Recommend
SequentialBuilder().participants([researcher, analyzer, advisor])
```

### Pattern 3: Divide and Conquer
```python
# Split task, process in parallel, combine results
WorkflowBuilder()
    .set_start_executor(splitter)
    .add_fan_out_edges(splitter, [worker1, worker2, worker3])
    .add_fan_in_edges([worker1, worker2, worker3], combiner)
```

### Pattern 4: Conditional Routing
```python
# Route to specialized agents based on query type
WorkflowBuilder()
    .add_switch_case_edge_group(router, [
        Case(lambda msg: "stock" in msg, target=stock_agent),
        Case(lambda msg: "weather" in msg, target=weather_agent),
        Default(target=general_agent)
    ])
```

---

## Documentation Links

- **Microsoft Agent Framework:** https://learn.microsoft.com/en-us/agent-framework/
- **Workflows Overview:** https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/overview
- **GitHub Repository:** https://github.com/microsoft/agent-framework

---

## Summary

✅ **Parallel execution is supported** via `ConcurrentBuilder`
✅ **Standalone agents are reusable** across multiple workflows
✅ **Multiple patterns available:** Sequential, Parallel, Conditional, Hybrid
✅ **Custom aggregation** with functions or agents
✅ **Performance benefits** from concurrent execution

**Your standalone agents (`weather_agent.py`, `stock_agent.py`) can be used in parallel workflows for faster execution and multiple perspectives!**
