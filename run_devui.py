#!/usr/bin/env python3
"""Launch DevUI with automatic agent and workflow discovery."""

import logging

# Setup logging first
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

from agent_framework.devui import serve
from agents import get_all_agents

# Try to import workflows (may fail if Azure credentials are not configured)
workflows_available = []
try:
    from workflows import (
        financial_workflow,
        simple_workflow,
        enhanced_workflow,
        parallel_workflow,
        parallel_with_callback,
    )
    workflows_available = [
        financial_workflow,
        simple_workflow,
        enhanced_workflow,
        parallel_workflow,
        parallel_with_callback,
    ]
except Exception as e:
    logger.warning(f"⚠️  Workflows not available (Azure credentials needed)")
    logger.info("💡 Continuing with agents only...")

logger.info("=" * 70)
logger.info("🚀 Starting Multi-Agent DevUI with Automatic Discovery")
logger.info("=" * 70)
logger.info("✨ All agents and tools are automatically discovered!")
logger.info("")

# Get all auto-discovered agents
agents = get_all_agents()

logger.info("📍 Available at: http://localhost:8080")
logger.info("")
logger.info(f"🤖 Auto-Discovered Agents ({len(agents)}):")
for agent_name, agent in agents.items():
    icon = "🌤️" if "weather" in agent_name else "📈" if "stock" in agent_name else "📧" if "email" in agent_name else "🔀" if "openrouter" in agent_name else "🤖"
    logger.info(f"   {icon}  {agent.name}")
logger.info("")

if workflows_available:
    logger.info("🔄 Workflows Available:")
    logger.info(f"   1. Financial Analysis (Sequential)")
    logger.info(f"   2. Simple Workflow (Sequential) - stock → weather")
    logger.info(f"   3. Enhanced Workflow (Sequential + Synthesis)")
    logger.info(f"   4. Parallel Workflow (Concurrent) - [stock || weather] ⚡")
    logger.info(f"   5. Parallel with Callback (Concurrent + Custom Aggregator) ⚡")
    logger.info("")
    logger.info("⚡ = Parallel execution (both agents run simultaneously)")
else:
    logger.info("⚠️  Workflows not available (Azure credentials required)")
    logger.info("💡 Tip: Configure Azure OpenAI or use OpenRouter agents instead")
    logger.info("")

logger.info("✨ = Just drop a YAML file in agents/ to add a new agent!")
logger.info("=" * 70)

# Build entities list - all agents plus workflows (if available)
entities = list(agents.values()) + workflows_available

# Launch server
serve(
    entities=entities,
    port=8080,
    auto_open=True
)
