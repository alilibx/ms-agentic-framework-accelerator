#!/usr/bin/env python
"""
Demo: Parallel Agent Execution

This script demonstrates the difference between sequential and parallel execution
of reusable agents in the Microsoft Agent Framework.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path to import from agents package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import weather_agent, stock_agent
from agent_framework import ConcurrentBuilder, SequentialBuilder


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def extract_text_from_messages(messages):
    """Extract text content from ChatMessage objects."""
    texts = []
    for msg in messages:
        if hasattr(msg, 'text'):
            texts.append(msg.text)
        elif hasattr(msg, 'content'):
            texts.append(str(msg.content))
    return texts


async def demo_sequential_execution():
    """Demo: Sequential execution (one agent at a time)."""
    print_separator("Sequential Execution Demo")
    print("Running agents ONE AT A TIME (stock → weather)\n")

    sequential_workflow = (
        SequentialBuilder()
        .participants([stock_agent, weather_agent])
        .build()
    )

    query = "Get AAPL stock price and weather in Cupertino"
    print(f"Query: {query}\n")

    start_time = time.time()
    result = await sequential_workflow.run(query)
    elapsed = time.time() - start_time

    print(f"\n⏱️  Execution time: {elapsed:.2f} seconds")
    print(f"📊 Output type: {type(result.get_outputs())}")
    print(f"📝 Number of outputs: {len(result.get_outputs())}")

    return result


async def demo_parallel_execution():
    """Demo: Parallel execution (all agents simultaneously)."""
    print_separator("Parallel Execution Demo")
    print("Running agents SIMULTANEOUSLY (stock || weather)\n")

    parallel_workflow = (
        ConcurrentBuilder()
        .participants([stock_agent, weather_agent])
        .build()
    )

    query = "Get AAPL stock price and weather in Cupertino"
    print(f"Query: {query}\n")

    start_time = time.time()
    result = await parallel_workflow.run(query)
    elapsed = time.time() - start_time

    print(f"\n⏱️  Execution time: {elapsed:.2f} seconds")
    print(f"📊 Output type: {type(result.get_outputs())}")

    outputs = result.get_outputs()
    if outputs and len(outputs) > 0:
        print(f"📝 Number of messages: {len(outputs[0])}")

    return result


async def demo_parallel_with_aggregator():
    """Demo: Parallel execution with custom aggregator."""
    print_separator("Parallel with Custom Aggregator Demo")
    print("Running agents in parallel with custom result aggregation\n")

    def format_results(results):
        """Custom aggregator to format parallel results."""
        output = []
        output.append("╔" + "═" * 68 + "╗")
        output.append("║" + " PARALLEL AGENT ANALYSIS RESULTS ".center(68) + "║")
        output.append("╠" + "═" * 68 + "╣")

        for i, result in enumerate(results, 1):
            if result.agent_run_response.messages:
                agent_name = result.executor_id
                last_message = result.agent_run_response.messages[-1]

                output.append("║")
                output.append(f"║  Agent {i}: {agent_name}")
                output.append("║  " + "─" * 64)

                # Extract text content
                if hasattr(last_message, 'text'):
                    text = last_message.text[:200] + "..." if len(last_message.text) > 200 else last_message.text
                    for line in text.split('\n'):
                        if line.strip():
                            output.append(f"║  {line[:64]}")

                output.append("║")

        output.append("╚" + "═" * 68 + "╝")
        return "\n".join(output)

    parallel_workflow = (
        ConcurrentBuilder()
        .participants([stock_agent, weather_agent])
        .with_aggregator(format_results)
        .build()
    )

    query = "Get MSFT stock analysis and weather forecast for Seattle"
    print(f"Query: {query}\n")

    start_time = time.time()
    result = await parallel_workflow.run(query)
    elapsed = time.time() - start_time

    outputs = result.get_outputs()
    if outputs and isinstance(outputs[0], str):
        print(outputs[0])

    print(f"\n⏱️  Execution time: {elapsed:.2f} seconds")

    return result


async def demo_performance_comparison():
    """Demo: Compare performance of sequential vs parallel."""
    print_separator("Performance Comparison")
    print("Running the same query with both patterns...\n")

    query = "Get OPENAI stock price and weather in San Francisco"

    # Sequential
    sequential_workflow = (
        SequentialBuilder()
        .participants([stock_agent, weather_agent])
        .build()
    )

    print("⏳ Running SEQUENTIAL execution...")
    seq_start = time.time()
    await sequential_workflow.run(query)
    seq_time = time.time() - seq_start

    # Parallel
    parallel_workflow = (
        ConcurrentBuilder()
        .participants([stock_agent, weather_agent])
        .build()
    )

    print("⏳ Running PARALLEL execution...")
    par_start = time.time()
    await parallel_workflow.run(query)
    par_time = time.time() - par_start

    # Results
    print(f"\n📊 Results:")
    print(f"   Sequential: {seq_time:.2f}s")
    print(f"   Parallel:   {par_time:.2f}s")

    if par_time < seq_time:
        speedup = seq_time / par_time
        print(f"   🚀 Speedup: {speedup:.2f}x faster with parallel execution!")
    else:
        print(f"   ℹ️  Times are similar (overhead may affect small tasks)")


async def main():
    """Run all demos."""
    print("\n")
    print("█" * 70)
    print("  Microsoft Agent Framework - Parallel Execution Demo".center(70))
    print("█" * 70)

    try:
        # Demo 1: Sequential
        await demo_sequential_execution()
        await asyncio.sleep(1)

        # Demo 2: Parallel
        await demo_parallel_execution()
        await asyncio.sleep(1)

        # Demo 3: Parallel with custom aggregator
        await demo_parallel_with_aggregator()
        await asyncio.sleep(1)

        # Demo 4: Performance comparison
        await demo_performance_comparison()

        print_separator("Summary")
        print("""
✅ Sequential Execution: Agents run one after another
   - Use when: Output from one agent feeds into the next
   - API: SequentialBuilder()

✅ Parallel Execution: Agents run simultaneously
   - Use when: Need multiple perspectives on same input
   - API: ConcurrentBuilder()
   - Benefits: Faster execution, multiple viewpoints

✅ Custom Aggregators: Control how parallel results are combined
   - Use callback functions or Executor classes
   - API: .with_aggregator(func_or_executor)

🎯 Key Takeaway: Standalone agents (weather_agent, stock_agent) can be
   reused in ANY workflow pattern - sequential, parallel, or hybrid!
        """)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
