#!/usr/bin/env python3
"""Launch DevUI with explicit agent registration."""

import logging
from agent_framework.devui import serve
from agents import weather_agent, stock_agent
from workflows import (
    financial_workflow,
    simple_workflow,
    enhanced_workflow,
    parallel_workflow,
    parallel_with_callback,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

logger.info("=" * 70)
logger.info("🚀 Starting Multi-Agent DevUI with Workflows")
logger.info("=" * 70)
logger.info("")
logger.info("📍 Available at: http://localhost:8080")
logger.info("")
logger.info("🤖 Standalone Agents:")
logger.info(f"   🌤️  {weather_agent.name}")
logger.info(f"   📈 {stock_agent.name}")
logger.info("")
logger.info("🔄 Workflows Available:")
logger.info(f"   1. Financial Analysis (Sequential) - from agentic_azure.py")
logger.info(f"   2. Simple Workflow (Sequential) - stock → weather")
logger.info(f"   3. Enhanced Workflow (Sequential + Synthesis)")
logger.info(f"   4. Parallel Workflow (Concurrent) - [stock || weather] ⚡")
logger.info(f"   5. Parallel with Callback (Concurrent + Custom Aggregator) ⚡")
logger.info("")
logger.info("⚡ = Parallel execution (both agents run simultaneously)")
logger.info("=" * 70)

# Launch server with agents and workflows
serve(
    entities=[
        # Standalone agents
        weather_agent,
        stock_agent,
        # Workflows
        financial_workflow,
        simple_workflow,
        enhanced_workflow,
        parallel_workflow,
        parallel_with_callback,
    ],
    port=8080,
    auto_open=True
)
