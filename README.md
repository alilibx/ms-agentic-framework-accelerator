# Agentic Microsoft Agent Framework Project

A multi-agent AI application built with Microsoft Agent Framework demonstrating sequential, parallel, and hybrid workflow patterns.

## 🏗️ Project Structure

```
agentic-ms/
├── agents/                     # Reusable agent definitions
│   ├── __init__.py
│   ├── weather_agent.py        # Weather information agent
│   └── stock_agent.py          # Stock market analysis agent
│
├── workflows/                  # Workflow orchestrations
│   ├── __init__.py
│   ├── financial_workflow.py   # Market → Weather → Investment workflow
│   └── reusable_workflows.py   # Sequential & parallel workflow examples
│
├── docs/                       # Documentation
│   ├── AGENT_WORKFLOW_ARCHITECTURE.md
│   └── PARALLEL_EXECUTION_QUICKSTART.md
│
├── demos/                      # Demo/example scripts
│   ├── demo_parallel_execution.py
│   └── workflow_runner.py
│
├── run_devui.py               # DevUI launcher (main entry point)
├── start_agent.sh             # Startup script
└── package.json               # NPM scripts configuration
```

## 🚀 Quick Start

### Start the DevUI

```bash
npm run agent
# or
./start_agent.sh
```

Then open: http://localhost:8080

### Stop the DevUI

```bash
npm run stop
```

### Run Demos

```bash
# Run parallel execution demo
python demos/demo_parallel_execution.py

# Run workflow visualization
python demos/workflow_runner.py
```

## 🤖 Available Agents

### Standalone Agents (agents/)
- **weather_agent** - Get weather forecasts and current conditions
- **stock_agent** - Get stock prices, analysis, and history

These agents can be:
- Used independently
- Combined in workflows
- Reused across multiple workflows

## 🔄 Available Workflows

### 1. Financial Analysis Workflow (Sequential)
Market Analyzer → Weather Analyst → Investment Advisor

### 2. Simple Sequential Workflow
Stock Agent → Weather Agent

### 3. Enhanced Sequential + Synthesis
Stock → Weather → Synthesis Agent (AI-powered aggregation)

### 4. ⚡ Parallel Execution
[Stock || Weather] - Both agents run simultaneously

### 5. ⚡ Parallel + Custom Aggregator
Parallel execution with custom result formatting

## 📚 Documentation

- **[Agent & Workflow Architecture](docs/AGENT_WORKFLOW_ARCHITECTURE.md)** - Comprehensive guide on agent reusability and workflow patterns
- **[Parallel Execution Quick Start](docs/PARALLEL_EXECUTION_QUICKSTART.md)** - Quick reference for parallel execution

## 💡 Key Concepts

### Agents are Reusable
Agents in `agents/` can be imported and used in any workflow:

```python
from agents import weather_agent, stock_agent
```

### Three Execution Patterns

**Sequential:**
```python
from agent_framework import SequentialBuilder
workflow = SequentialBuilder().participants([agent1, agent2]).build()
```

**Parallel (⚡ Faster):**
```python
from agent_framework import ConcurrentBuilder
workflow = ConcurrentBuilder().participants([agent1, agent2]).build()
```

**Custom:**
```python
from agent_framework import WorkflowBuilder
workflow = (
    WorkflowBuilder()
    .set_start_executor(agent1)
    .add_fan_out_edges(agent1, [agent2, agent3])  # Parallel
    .build()
)
```

## 🎯 Example Queries

Try these in the DevUI:

**For Parallel Workflows** (notice the speed!):
- "Get AAPL stock price and weather in Cupertino"
- "Analyze MSFT stock and weather in Seattle"

**For Sequential Workflows**:
- "Provide investment advice considering market and weather"
- "What's the market outlook for tech stocks?"

## 📦 NPM Scripts

```bash
npm run agent     # Start DevUI
npm run stop      # Stop all processes
npm run restart   # Restart DevUI
npm run status    # Check if agent is running
npm run workflow  # Run workflow demo
```

## 🛠️ Technology Stack

- **Microsoft Agent Framework** - AI agent orchestration
- **Azure OpenAI** - LLM backend (GPT-4o)
- **Python 3.10+** - Runtime
- **DevUI** - Web-based interaction interface

## 📖 Learning Resources

1. Start with `docs/PARALLEL_EXECUTION_QUICKSTART.md` for quick examples
2. Read `docs/AGENT_WORKFLOW_ARCHITECTURE.md` for comprehensive understanding
3. Explore code in `agents/` and `workflows/` directories
4. Run demos in `demos/` to see workflows in action

## 🎨 Workflow Visualization

```
Sequential:
Input → Agent1 → Agent2 → Agent3 → Output

Parallel:
          ┌─ Agent1 ─┐
Input ─→  ├─ Agent2 ─┤  → Aggregator → Output
          └─ Agent3 ─┘

Hybrid:
Input → Agent1 → [Agent2 || Agent3] → Agent4 → Output
```

## 🔧 Development

### Adding a New Agent

1. Create file in `agents/my_agent.py`
2. Export in `agents/__init__.py`
3. Import in workflows: `from agents import my_agent`

### Adding a New Workflow

1. Create file in `workflows/my_workflow.py`
2. Import agents: `from agents import agent1, agent2`
3. Build workflow using WorkflowBuilder/ConcurrentBuilder/SequentialBuilder
4. Export in `workflows/__init__.py`
5. Register in `run_devui.py`

## 📄 License

MIT

---

**Built with ❤️ using Microsoft Agent Framework**
