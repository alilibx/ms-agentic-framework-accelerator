"""Workflow Definitions.

This package contains workflow orchestrations that combine
multiple agents in different patterns (sequential, parallel, hybrid).

The comprehensive_workflow module demonstrates 6 different workflow patterns:
1. Sequential Execution
2. Parallel Execution
3. Sequential + Synthesis
4. Parallel + Synthesis
5. Comprehensive Business Workflow
6. Multi-Domain Parallel
"""

from .comprehensive_workflow import (
    # Workflows
    sequential_workflow,
    parallel_workflow,
    enhanced_sequential,
    parallel_with_synthesis_workflow,
    comprehensive_business_workflow,
    multi_domain_parallel,
    # Agents
    market_analyzer,
    investment_advisor,
    synthesis_agent,
    # Examples
    example_sequential,
    example_parallel,
    example_synthesis,
    example_comprehensive,
    example_streaming,
)

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
    # Examples
    "example_sequential",
    "example_parallel",
    "example_synthesis",
    "example_comprehensive",
    "example_streaming",
]
