#!/usr/bin/env python3
"""Workflow runner with visualization capabilities."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path to import from workflows package
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.comprehensive_workflow import (
    sequential_workflow,
    parallel_workflow,
    enhanced_sequential,
    market_analyzer,
    investment_advisor,
    synthesis_agent
)
from agent_framework import WorkflowExecutor, WorkflowViz

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_workflow_example():
    """Run the comprehensive workflow examples."""
    logger.info("🚀 Comprehensive Workflow Examples")
    logger.info("=" * 50)
    logger.info("📊 Available Workflows:")
    logger.info("  1. Sequential: Stock → Weather → Investment Advisor")
    logger.info("  2. Parallel: [Stock || Weather || Market] → Combined Report")
    logger.info("  3. Enhanced Sequential: Multiple steps → AI Synthesis")
    logger.info("  4. Parallel + Synthesis: Fast parallel → AI combination")
    logger.info("  5. Comprehensive Business: Complete cross-domain process")
    logger.info("  6. Multi-Domain Parallel: Different systems simultaneously")
    logger.info("✅ All workflows ready for execution in DevUI")

    return "Workflow structures created successfully"

def show_workflow_visualization():
    """Display workflow visualization."""
    logger.info("🎨 Workflow Visualization")
    logger.info("=" * 50)

    # Visualize sequential workflow
    workflow_viz = WorkflowViz(sequential_workflow)

    # Generate Mermaid diagram
    mermaid_diagram = workflow_viz.to_mermaid()
    logger.info("📊 Sequential Workflow - Mermaid Diagram:")
    logger.info(mermaid_diagram)

    # Generate DOT diagram
    dot_diagram = workflow_viz.to_digraph()
    logger.info("\n📈 Sequential Workflow - DOT Diagram:")
    logger.info(dot_diagram)

    # Export visualization
    try:
        workflow_viz.export(format="svg", filename="sequential_workflow.svg")
        logger.info("✅ Workflow visualization exported to: sequential_workflow.svg")
    except Exception as e:
        logger.warning(f"⚠️ Could not export SVG: {e}")
        logger.info("💡 Install Graphviz to enable SVG export: brew install graphviz")

def main():
    """Main function to run workflow and show visualization."""
    logger.info("🏦 Comprehensive Workflow Demo")
    logger.info("=" * 50)

    # Show workflow structure
    show_workflow_visualization()

    # Run the workflow
    logger.info("\n🔄 Workflow Structures...")
    run_workflow_example()

if __name__ == "__main__":
    main()
