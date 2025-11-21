#!/usr/bin/env python3
"""Launch DevUI with automatic agent and workflow discovery."""

import logging
import os

# Suppress verbose discovery logs
os.environ['PYTHONWARNINGS'] = 'ignore'
logging.basicConfig(level=logging.WARNING, format="%(message)s")

from agent_framework.devui import serve
from agents import get_all_agents, get_discovery_data
from utils import StartupLogger

# Get discovery data
discovery = get_discovery_data()
agents = discovery['agents']
tools_by_domain = discovery['tools_by_domain']

# Collect warnings
warnings = []

# Try to import workflows (may fail if Azure credentials are not configured)
workflows_available = []
try:
    from workflows import (
        sequential_workflow,
        parallel_workflow,
        enhanced_sequential,
        parallel_with_synthesis_workflow,
        comprehensive_business_workflow,
        multi_domain_parallel,
    )
    workflows_available = [
        sequential_workflow,
        parallel_workflow,
        enhanced_sequential,
        parallel_with_synthesis_workflow,
        comprehensive_business_workflow,
        multi_domain_parallel,
    ]
except Exception as e:
    warnings.append("Workflows not available (Azure credentials required)")
    warnings.append("Tip: Configure Azure OpenAI or use OpenRouter agents")

# Print beautiful startup summary
StartupLogger.print_startup_summary(
    tools_by_domain=tools_by_domain,
    agents=agents,
    agent_tools_map=discovery['agent_tools_map'],
    warnings=warnings if warnings else None
)

# Build entities list - all agents plus workflows (if available)
entities = list(agents.values()) + workflows_available

# Launch server (suppress its startup logs)
serve(
    entities=entities,
    port=8080,
    auto_open=True
)
