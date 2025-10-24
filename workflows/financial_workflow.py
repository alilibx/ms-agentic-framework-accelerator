# Copyright (c) Microsoft. All rights reserved.
"""Financial Analysis Workflow for Agent Framework DevUI."""

import os
from typing import Annotated
from datetime import datetime, timedelta
import random

from agent_framework import (
    ChatAgent, 
    WorkflowBuilder, 
    WorkflowViz,
    WorkflowExecutor,
    WorkflowContext
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential


# Helper functions for the workflow
def analyze_market_conditions() -> str:
    """Analyze current market conditions."""
    conditions = ["bullish", "bearish", "volatile", "stable"]
    condition = random.choice(conditions)
    return f"📊 Market Analysis: Current market conditions are {condition} with moderate volatility."


def get_weather_impact() -> str:
    """Get weather impact on markets."""
    impacts = ["positive", "negative", "neutral"]
    impact = random.choice(impacts)
    return f"🌤️ Weather Impact: Current weather patterns suggest a {impact} impact on energy and agriculture sectors."


def get_sector_performance() -> str:
    """Get sector performance data."""
    sectors = {
        "Technology": random.uniform(-2, 5),
        "Healthcare": random.uniform(-1, 3),
        "Energy": random.uniform(-3, 4),
        "Finance": random.uniform(-2, 2)
    }
    
    result = "📈 Sector Performance:\n"
    for sector, change in sectors.items():
        emoji = "📈" if change > 0 else "📉"
        result += f"{emoji} {sector}: {change:+.2f}%\n"
    
    return result


def generate_investment_recommendation() -> str:
    """Generate investment recommendations based on analysis."""
    recommendations = [
        "💡 Consider diversifying into technology and healthcare sectors",
        "⚠️ Reduce exposure to energy sector due to volatility",
        "🎯 Focus on blue-chip stocks with strong fundamentals",
        "📊 Monitor market conditions closely for entry opportunities"
    ]
    
    return f"🎯 Investment Recommendations:\n" + "\n".join(random.sample(recommendations, 2))


# Create workflow executors (agents)
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

weather_analyst = ChatAgent(
    name="Weather Analyst", 
    description="Analyzes weather impact on markets",
    instructions="You are a weather analyst specializing in market impact. Analyze how weather affects different sectors.",
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm", 
        credential=AzureCliCredential(),
    ),
    tools=[get_weather_impact]
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

# Create the workflow - Sequential flow
workflow = (
    WorkflowBuilder(
        name="Financial Analysis Workflow",
        description="Market Analysis → Weather Impact → Investment Advice (Sequential)"
    )
    .set_start_executor(market_analyzer)
    .add_edge(market_analyzer, weather_analyst)
    .add_edge(weather_analyst, investment_advisor)
    .build()
)

# Create workflow visualization
workflow_viz = WorkflowViz(workflow)

# Export for DevUI
__all__ = ["workflow", "workflow_viz", "market_analyzer", "weather_analyst", "investment_advisor"]
