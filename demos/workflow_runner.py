#!/usr/bin/env python3
"""Workflow runner with visualization capabilities."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path to import from workflows package
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.financial_workflow import workflow, workflow_viz, market_analyzer, weather_analyst, investment_advisor
from agent_framework import WorkflowExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_workflow_example():
    """Run the financial analysis workflow."""
    logger.info("🚀 Financial Analysis Workflow Structure")
    logger.info("=" * 50)
    logger.info("📊 Workflow: Market Analyzer → Weather Analyst → Investment Advisor")
    logger.info("🔄 This workflow analyzes market conditions, weather impact, and provides investment recommendations")
    logger.info("✅ Workflow is ready for execution in DevUI")
    
    return "Workflow structure created successfully"

def show_workflow_visualization():
    """Display workflow visualization."""
    logger.info("🎨 Workflow Visualization")
    logger.info("=" * 50)
    
    # Generate Mermaid diagram
    mermaid_diagram = workflow_viz.to_mermaid()
    logger.info("📊 Mermaid Diagram:")
    logger.info(mermaid_diagram)
    
    # Generate DOT diagram
    dot_diagram = workflow_viz.to_digraph()
    logger.info("\n📈 DOT Diagram:")
    logger.info(dot_diagram)
    
    # Export visualization
    try:
        workflow_viz.export(format="svg", filename="financial_workflow.svg")
        logger.info("✅ Workflow visualization exported to: financial_workflow.svg")
    except Exception as e:
        logger.warning(f"⚠️ Could not export SVG: {e}")
        logger.info("💡 Install Graphviz to enable SVG export: brew install graphviz")

def main():
    """Main function to run workflow and show visualization."""
    logger.info("🏦 Financial Analysis Workflow Demo")
    logger.info("=" * 50)
    
    # Show workflow structure
    show_workflow_visualization()
    
    # Run the workflow
    logger.info("\n🔄 Workflow Structure...")
    run_workflow_example()

if __name__ == "__main__":
    main()
