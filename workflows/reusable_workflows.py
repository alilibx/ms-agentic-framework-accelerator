# Copyright (c) Microsoft. All rights reserved.
"""Example workflow demonstrating how to reuse standalone agents.

This file shows how weather_agent.py and stock_agent.py can be used
in workflows instead of defining agents inline.
"""

from agents import weather_agent, stock_agent
from agent_framework import WorkflowBuilder, ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential


# Example 1: Simple Sequential Workflow Using Standalone Agents
# ============================================================
# This workflow chains the stock agent and weather agent together

simple_workflow = (
    WorkflowBuilder(
        name="Simple Sequential Workflow",
        description="Stock Agent → Weather Agent (Sequential execution)"
    )
    .set_start_executor(stock_agent)      # Reuse stock_agent from stock_agent.py
    .add_edge(stock_agent, weather_agent)  # Reuse weather_agent from weather_agent.py
    .build()
)


# Example 2: Adding a Synthesis Agent to Standalone Agents
# =========================================================
# This shows how to mix reusable standalone agents with a new synthesizer

# Create a synthesizer agent that combines insights
synthesis_agent = ChatAgent(
    name="Investment Synthesis Agent",
    description="Synthesizes stock and weather data into actionable recommendations",
    instructions="""
    You receive stock market analysis and weather information.
    Your job is to:
    1. Combine insights from both sources
    2. Identify correlations (e.g., weather impact on energy stocks)
    3. Provide clear, actionable investment recommendations

    Be specific and reference both the stock data and weather data in your recommendations.
    """,
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
)

# Build workflow: Stock Agent → Weather Agent → Synthesis Agent
enhanced_workflow = (
    WorkflowBuilder(
        name="Enhanced Sequential + Synthesis",
        description="Stock → Weather → Synthesis Agent (Sequential with AI synthesis)"
    )
    .set_start_executor(stock_agent)        # Reusable standalone agent
    .add_edge(stock_agent, weather_agent)    # Reusable standalone agent
    .add_edge(weather_agent, synthesis_agent) # New agent for this workflow
    .build()
)


# Example 3: Parallel Analysis Using ConcurrentBuilder
# =====================================================
# Run multiple agents in parallel for faster, multi-perspective analysis

from agent_framework import ConcurrentBuilder

# Simple parallel execution - both agents analyze the same input simultaneously
parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .build()
)
# Set workflow name after building (ConcurrentBuilder may not support name in constructor)
parallel_workflow.name = "⚡ Parallel Execution"
parallel_workflow.description = "[Stock || Weather] - Both agents run simultaneously"

# Parallel execution with custom aggregation using synthesis_agent
# Note: ChatAgent cannot be used directly as aggregator, use callback or Executor instead
# parallel_with_synthesis = (
#     ConcurrentBuilder()
#     .participants([stock_agent, weather_agent])
#     .with_aggregator(synthesis_agent)  # Aggregates parallel results
#     .build()
# )

# Parallel execution with callback function aggregator
def combine_parallel_results(results):
    """Custom function to combine results from parallel agent execution."""
    combined = ["=== Parallel Analysis Results ===\n"]

    for i, result in enumerate(results, 1):
        if result.agent_run_response.messages:
            agent_name = result.executor_id
            last_message = result.agent_run_response.messages[-1].text
            combined.append(f"\n--- Agent {i}: {agent_name} ---")
            combined.append(last_message)

    return "\n".join(combined)

parallel_with_callback = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent])
    .with_aggregator(combine_parallel_results)
    .build()
)
# Set workflow name after building
parallel_with_callback.name = "⚡ Parallel + Custom Aggregator"
parallel_with_callback.description = "[Stock || Weather] → Custom Formatter (Parallel with callback)"


# Usage Examples
# ==============

async def example_simple_workflow():
    """Run the simple workflow with stock and weather agents."""
    print("=== Simple Workflow Example ===")

    # This will:
    # 1. Get stock information from stock_agent
    # 2. Get weather information from weather_agent
    result = await simple_workflow.run(
        "What's the stock price for AAPL and the weather in Cupertino?"
    )

    outputs = result.get_outputs()
    print("Workflow outputs:", outputs)
    return result


async def example_enhanced_workflow():
    """Run the enhanced workflow with synthesis."""
    print("=== Enhanced Workflow Example ===")

    # This will:
    # 1. Analyze stock data (stock_agent)
    # 2. Get weather information (weather_agent)
    # 3. Synthesize insights (synthesis_agent)
    result = await enhanced_workflow.run(
        "Analyze AAPL and MSFT stocks, check weather conditions in California, "
        "and provide investment recommendations considering weather impacts on tech sector."
    )

    outputs = result.get_outputs()
    print("Workflow outputs:", outputs)
    return result


async def example_streaming_workflow():
    """Run the workflow with streaming to see intermediate results."""
    print("=== Streaming Workflow Example ===")

    async for event in enhanced_workflow.run_stream(
        "Get OPENAI stock analysis and weather forecast for Seattle"
    ):
        print(f"Event type: {type(event).__name__}")
        if hasattr(event, 'data'):
            print(f"Event data: {event.data}")


async def example_parallel_workflow():
    """Run agents in parallel for faster execution."""
    print("=== Parallel Workflow Example ===")

    # This will run stock_agent and weather_agent simultaneously
    result = await parallel_workflow.run(
        "Get AAPL stock price and weather in California"
    )

    outputs = result.get_outputs()
    print("Parallel workflow outputs:", outputs)
    return result


# async def example_parallel_with_synthesis():
#     """Run parallel workflow with synthesis agent aggregating results."""
#     print("=== Parallel with Synthesis Example ===")

#     # This will:
#     # 1. Run stock_agent and weather_agent in parallel
#     # 2. Synthesis agent combines their outputs
#     result = await parallel_with_synthesis.run(
#         "Analyze MSFT stock performance and weather conditions in Seattle. "
#         "How might weather affect tech sector operations?"
#     )

#     outputs = result.get_outputs()
#     print("Synthesized output:", outputs)
#     return result


async def example_parallel_with_callback():
    """Run parallel workflow with custom callback aggregator."""
    print("=== Parallel with Callback Example ===")

    result = await parallel_with_callback.run(
        "Compare OPENAI and AAPL stocks, and check weather in San Francisco"
    )

    outputs = result.get_outputs()
    print("Combined output:", outputs)
    return result


# Comparison with agentic_azure.py approach
# =========================================

# OLD APPROACH (agentic_azure.py):
# - Agents defined inline in the same file as the workflow
# - Cannot reuse agents in other workflows
# - All code in one file
# - Sequential execution only

# NEW APPROACH (this file):
# - Import reusable agents from weather_agent.py and stock_agent.py
# - Can use these agents in multiple different workflows
# - Clean separation: agent definitions vs workflow orchestration
# - Mix reusable agents with workflow-specific agents as needed
# - Support for multiple execution patterns:
#   * Sequential: WorkflowBuilder with add_edge
#   * Parallel: ConcurrentBuilder for simultaneous execution
#   * Hybrid: Combine sequential and parallel patterns

# PARALLEL EXECUTION BENEFITS:
# ✓ Faster execution - agents run simultaneously
# ✓ Multiple perspectives - different agents analyze the same input
# ✓ Flexible aggregation - combine results with custom logic
# ✓ Scales with compute resources


# For DevUI registration
# ======================
# You can register these workflows in run_devui.py:
#
# from example_reusable_workflow import simple_workflow, enhanced_workflow
#
# serve(
#     entities=[
#         weather_agent,
#         stock_agent,
#         simple_workflow,
#         enhanced_workflow,
#     ],
#     port=8080
# )


# Export for use in other files
__all__ = [
    # Workflows
    "simple_workflow",
    "enhanced_workflow",
    "parallel_workflow",
    # "parallel_with_synthesis",  # Commented out - ChatAgent not compatible as aggregator
    "parallel_with_callback",
    # Agents
    "synthesis_agent",
    # Example functions
    "example_simple_workflow",
    "example_enhanced_workflow",
    "example_streaming_workflow",
    "example_parallel_workflow",
    # "example_parallel_with_synthesis",  # Commented out
    "example_parallel_with_callback",
    # Utility functions
    "combine_parallel_results",
]


# For DevUI registration
# ======================
# You can register these workflows in run_devui.py:
#
# from example_reusable_workflow import (
#     simple_workflow,
#     enhanced_workflow,
#     parallel_workflow,
#     parallel_with_synthesis,
# )
#
# serve(
#     entities=[
#         weather_agent,
#         stock_agent,
#         simple_workflow,
#         enhanced_workflow,
#         parallel_workflow,
#         parallel_with_synthesis,
#     ],
#     port=8080
# )


# Main entry point for testing
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("Agent Workflow Examples - Demonstrating Reusable Agents")
    print("=" * 70)
    print("\nThis file demonstrates how to reuse standalone agents in workflows.")
    print("\nAvailable workflow patterns:")
    print("  1. Sequential: agent1 → agent2 → agent3")
    print("  2. Enhanced: agent1 → agent2 → synthesis")
    print("  3. Parallel: [agent1, agent2] → aggregator (RUNS SIMULTANEOUSLY)")
    print("\nTo run examples:")
    print("\n  Sequential workflow:")
    print("  python -c 'import asyncio; from example_reusable_workflow import example_simple_workflow; asyncio.run(example_simple_workflow())'")
    print("\n  Enhanced workflow:")
    print("  python -c 'import asyncio; from example_reusable_workflow import example_enhanced_workflow; asyncio.run(example_enhanced_workflow())'")
    print("\n  Parallel workflow:")
    print("  python -c 'import asyncio; from example_reusable_workflow import example_parallel_workflow; asyncio.run(example_parallel_workflow())'")
    print("\n  Parallel with callback aggregator:")
    print("  python -c 'import asyncio; from example_reusable_workflow import example_parallel_with_callback; asyncio.run(example_parallel_with_callback())'")
    print("\nOr register in DevUI by adding to run_devui.py")
    print("=" * 70)
