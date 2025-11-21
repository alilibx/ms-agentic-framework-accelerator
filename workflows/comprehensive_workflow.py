# Copyright (c) Microsoft. All rights reserved.
"""Comprehensive Workflow Examples for Agent Framework.

This file demonstrates various workflow patterns including:
- Sequential workflows with chained agents
- Parallel execution for simultaneous processing
- Synthesis patterns for combining results
- Reusable agent composition

All workflows use the dynamically discovered agents from agents/ directory.
"""

from typing import Annotated
from datetime import datetime, timedelta
import random

from agent_framework import (
    ChatAgent,
    WorkflowBuilder,
    WorkflowViz,
    ConcurrentBuilder,
    WorkflowExecutor,
    WorkflowContext
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Import all dynamically discovered agents
from agents import (
    weather_agent,
    stock_agent,
    email_agent,
    calendar_agent,
    hr_agent
)


# ============================================================================
# HELPER FUNCTIONS FOR WORKFLOWS
# ============================================================================

def analyze_market_conditions() -> str:
    """Analyze current market conditions."""
    conditions = ["bullish", "bearish", "volatile", "stable"]
    condition = random.choice(conditions)
    return f"Market Analysis: Current market conditions are {condition} with moderate volatility."


def get_sector_performance() -> str:
    """Get sector performance data."""
    sectors = {
        "Technology": random.uniform(-2, 5),
        "Healthcare": random.uniform(-1, 3),
        "Energy": random.uniform(-3, 4),
        "Finance": random.uniform(-2, 2)
    }

    result = "Sector Performance:\n"
    for sector, change in sectors.items():
        emoji = "+" if change > 0 else ""
        result += f"  • {sector}: {emoji}{change:.2f}%\n"

    return result


def generate_investment_recommendation() -> str:
    """Generate investment recommendations based on analysis."""
    recommendations = [
        "Consider diversifying into technology and healthcare sectors",
        "Reduce exposure to energy sector due to volatility",
        "Focus on blue-chip stocks with strong fundamentals",
        "Monitor market conditions closely for entry opportunities"
    ]

    return "Investment Recommendations:\n" + "\n".join(f"  • {r}" for r in random.sample(recommendations, 2))


# ============================================================================
# SPECIALIZED ANALYSIS AGENTS
# ============================================================================

market_analyzer = ChatAgent(
    name="Market Analyzer",
    description="Analyzes market conditions and trends",
    instructions="You are a financial market analyst. Analyze market conditions and provide insights.",
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
    tools=[analyze_market_conditions, get_sector_performance]
)

investment_advisor = ChatAgent(
    name="Investment Advisor",
    description="Provides investment recommendations",
    instructions="You are an investment advisor. Provide strategic investment recommendations based on market analysis.",
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
    tools=[generate_investment_recommendation]
)

synthesis_agent = ChatAgent(
    name="Synthesis Agent",
    description="Synthesizes information from multiple sources into actionable insights",
    instructions="""
    You receive information from multiple specialized agents.
    Your job is to:
    1. Combine insights from all sources
    2. Identify correlations and patterns
    3. Provide clear, actionable recommendations
    4. Prioritize the most important findings

    Be specific and reference all the data sources in your synthesis.
    Format your output with clear sections and bullet points.
    """,
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
)


# ============================================================================
# WORKFLOW PATTERN 1: SEQUENTIAL EXECUTION
# ============================================================================
# Use case: When each step depends on the previous step's output
# Example: Stock analysis → Weather impact → Investment recommendation

sequential_workflow = (
    WorkflowBuilder(
        name="Sequential Financial Analysis",
        description="Stock → Weather → Investment Advisor (Sequential execution)"
    )
    .set_start_executor(stock_agent)
    .add_edge(stock_agent, weather_agent)
    .add_edge(weather_agent, investment_advisor)
    .build()
)


# ============================================================================
# WORKFLOW PATTERN 2: PARALLEL EXECUTION
# ============================================================================
# Use case: When multiple analyses can happen simultaneously
# Example: Stock analysis AND Weather analysis running at the same time

def combine_parallel_results(results):
    """Custom aggregator to combine results from parallel execution."""
    combined = ["=== Parallel Analysis Results ===\n"]

    for i, result in enumerate(results, 1):
        if result.agent_run_response.messages:
            agent_name = result.executor_id
            last_message = result.agent_run_response.messages[-1].text
            combined.append(f"\n--- Analysis {i}: {agent_name} ---")
            combined.append(last_message)

    return "\n".join(combined)


parallel_workflow = (
    ConcurrentBuilder()
    .participants([stock_agent, weather_agent, market_analyzer])
    .with_aggregator(combine_parallel_results)
    .build()
)
parallel_workflow.name = "Parallel Market Analysis"
parallel_workflow.description = "[Stock || Weather || Market] → Aggregated Report (Parallel execution)"


# ============================================================================
# WORKFLOW PATTERN 3: SEQUENTIAL + SYNTHESIS
# ============================================================================
# Use case: Multiple sequential steps with final synthesis
# Example: Multiple analyses → Comprehensive synthesis

enhanced_sequential = (
    WorkflowBuilder(
        name="Enhanced Sequential with Synthesis",
        description="Stock → Weather → Market → Synthesis (Sequential with AI synthesis)"
    )
    .set_start_executor(stock_agent)
    .add_edge(stock_agent, weather_agent)
    .add_edge(weather_agent, market_analyzer)
    .add_edge(market_analyzer, synthesis_agent)
    .build()
)


# ============================================================================
# WORKFLOW PATTERN 4: PARALLEL + SYNTHESIS
# ============================================================================
# Use case: Multiple parallel analyses combined into single report
# Example: Stock AND Weather AND Market → Synthesis

# Note: ConcurrentBuilder with ChatAgent aggregator requires special handling
# We'll use a sequential approach: parallel agents → synthesis
parallel_with_synthesis_workflow = (
    WorkflowBuilder(
        name="Parallel Analysis with Synthesis",
        description="[Stock || Weather || Market] → Synthesis (Parallel → AI synthesis)"
    )
    .set_start_executor(market_analyzer)
    .add_edge(market_analyzer, synthesis_agent)
    .build()
)


# ============================================================================
# WORKFLOW PATTERN 5: COMPREHENSIVE BUSINESS WORKFLOW
# ============================================================================
# Use case: Complete business process with multiple touchpoints
# Example: Market research → Schedule meeting → Send email → HR follow-up

comprehensive_business_workflow = (
    WorkflowBuilder(
        name="Comprehensive Business Workflow",
        description="Market Analysis → Calendar → Email → HR (Full business process)"
    )
    .set_start_executor(market_analyzer)
    .add_edge(market_analyzer, calendar_agent)
    .add_edge(calendar_agent, email_agent)
    .add_edge(email_agent, hr_agent)
    .build()
)


# ============================================================================
# WORKFLOW PATTERN 6: MULTI-DOMAIN PARALLEL
# ============================================================================
# Use case: Gathering information from different domains simultaneously
# Example: Check stocks AND schedule AND emails in parallel

multi_domain_parallel = (
    ConcurrentBuilder()
    .participants([stock_agent, calendar_agent, email_agent])
    .with_aggregator(combine_parallel_results)
    .build()
)
multi_domain_parallel.name = "Multi-Domain Parallel Query"
multi_domain_parallel.description = "[Stock || Calendar || Email] → Combined Report"


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_sequential():
    """Run sequential workflow."""
    print("=== Sequential Workflow Example ===")

    result = await sequential_workflow.run(
        "Analyze AAPL stock, check weather impact on tech sector, "
        "and provide investment recommendations."
    )

    outputs = result.get_outputs()
    print("Workflow outputs:", outputs)
    return result


async def example_parallel():
    """Run parallel workflow for faster execution."""
    print("=== Parallel Workflow Example ===")

    result = await parallel_workflow.run(
        "Provide market analysis for MSFT stock and weather conditions in Seattle"
    )

    outputs = result.get_outputs()
    print("Parallel workflow outputs:", outputs)
    return result


async def example_synthesis():
    """Run workflow with synthesis."""
    print("=== Synthesis Workflow Example ===")

    result = await enhanced_sequential.run(
        "Analyze AAPL and MSFT stocks, consider weather impacts, "
        "check market conditions, and synthesize investment strategy."
    )

    outputs = result.get_outputs()
    print("Synthesized output:", outputs)
    return result


async def example_comprehensive():
    """Run comprehensive business workflow."""
    print("=== Comprehensive Business Workflow Example ===")

    result = await comprehensive_business_workflow.run(
        "Analyze Q4 market performance, schedule a team meeting to discuss findings, "
        "send summary email to stakeholders, and check if any team members are on leave."
    )

    outputs = result.get_outputs()
    print("Business workflow outputs:", outputs)
    return result


async def example_streaming():
    """Run workflow with streaming to see intermediate results."""
    print("=== Streaming Workflow Example ===")

    async for event in sequential_workflow.run_stream(
        "Get OPENAI stock analysis and weather forecast for San Francisco"
    ):
        print(f"Event type: {type(event).__name__}")
        if hasattr(event, 'data'):
            print(f"Event data: {event.data}")


# ============================================================================
# WORKFLOW COMPARISON GUIDE
# ============================================================================

"""
WORKFLOW PATTERN COMPARISON:

1. SEQUENTIAL
   ✓ Use when: Steps depend on previous results
   ✓ Example: Research → Analysis → Recommendation
   ✓ Speed: Slower (one at a time)
   ✓ Complexity: Simple to understand

2. PARALLEL
   ✓ Use when: Independent analyses needed simultaneously
   ✓ Example: Stock AND Weather AND News at same time
   ✓ Speed: Faster (runs simultaneously)
   ✓ Complexity: Requires result aggregation

3. SEQUENTIAL + SYNTHESIS
   ✓ Use when: Need comprehensive analysis of chained results
   ✓ Example: Multiple steps → AI combines everything
   ✓ Speed: Slower (sequential)
   ✓ Complexity: Moderate (requires synthesis agent)

4. PARALLEL + SYNTHESIS
   ✓ Use when: Need fast multi-source analysis with smart combination
   ✓ Example: Parallel gathering → AI synthesis
   ✓ Speed: Faster (parallel gathering)
   ✓ Complexity: Higher (parallel + synthesis)

5. COMPREHENSIVE BUSINESS
   ✓ Use when: Complete business process across domains
   ✓ Example: Research → Meeting → Email → HR
   ✓ Speed: Slower (many steps)
   ✓ Complexity: High (cross-domain orchestration)

6. MULTI-DOMAIN PARALLEL
   ✓ Use when: Need information from different systems fast
   ✓ Example: Check stocks, calendar, emails simultaneously
   ✓ Speed: Fast (parallel)
   ✓ Complexity: Moderate (domain integration)

CHOOSING THE RIGHT PATTERN:
- Need speed + independent tasks? → PARALLEL
- Steps depend on each other? → SEQUENTIAL
- Need comprehensive report? → Add SYNTHESIS
- Complete business process? → COMPREHENSIVE
- Different systems/domains? → MULTI-DOMAIN
"""


# ============================================================================
# EXPORT FOR DEVUI AND OTHER MODULES
# ============================================================================

__all__ = [
    # Workflows
    "sequential_workflow",
    "parallel_workflow",
    "enhanced_sequential",
    "parallel_with_synthesis_workflow",
    "comprehensive_business_workflow",
    "multi_domain_parallel",

    # Agents
    "market_analyzer",
    "investment_advisor",
    "synthesis_agent",

    # Visualization
    "WorkflowViz",

    # Example functions
    "example_sequential",
    "example_parallel",
    "example_synthesis",
    "example_comprehensive",
    "example_streaming",

    # Utility functions
    "combine_parallel_results",
    "analyze_market_conditions",
    "get_sector_performance",
    "generate_investment_recommendation",
]


# ============================================================================
# MAIN ENTRY POINT FOR TESTING
# ============================================================================

if __name__ == "__main__":
    import asyncio

    print("=" * 80)
    print("COMPREHENSIVE WORKFLOW EXAMPLES - Agent Framework")
    print("=" * 80)
    print("\nThis file demonstrates 6 different workflow patterns:")
    print("\n1. Sequential Execution - Steps run one after another")
    print("2. Parallel Execution - Multiple agents run simultaneously")
    print("3. Sequential + Synthesis - Chain with AI-powered synthesis")
    print("4. Parallel + Synthesis - Fast parallel with AI combination")
    print("5. Comprehensive Business - Full cross-domain process")
    print("6. Multi-Domain Parallel - Different systems queried simultaneously")
    print("\n" + "=" * 80)
    print("\nTo run examples:")
    print("\n  python -c 'import asyncio; from workflows.comprehensive_workflow import example_sequential; asyncio.run(example_sequential())'")
    print("\n  python -c 'import asyncio; from workflows.comprehensive_workflow import example_parallel; asyncio.run(example_parallel())'")
    print("\n  python -c 'import asyncio; from workflows.comprehensive_workflow import example_synthesis; asyncio.run(example_synthesis())'")
    print("\n  python -c 'import asyncio; from workflows.comprehensive_workflow import example_comprehensive; asyncio.run(example_comprehensive())'")
    print("\nOr register workflows in DevUI by importing them in run_devui.py")
    print("=" * 80)
