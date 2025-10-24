"""Workflow Definitions.

This package contains workflow orchestrations that combine
multiple agents in different patterns (sequential, parallel, hybrid).
"""

from .financial_workflow import (
    workflow as financial_workflow,
    market_analyzer,
    weather_analyst,
    investment_advisor,
)

from .reusable_workflows import (
    simple_workflow,
    enhanced_workflow,
    parallel_workflow,
    parallel_with_callback,
    synthesis_agent,
)

__all__ = [
    # Financial workflow and its agents
    "financial_workflow",
    "market_analyzer",
    "weather_analyst",
    "investment_advisor",
    # Reusable workflows
    "simple_workflow",
    "enhanced_workflow",
    "parallel_workflow",
    "parallel_with_callback",
    # Agents
    "synthesis_agent",
]
