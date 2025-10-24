# Copyright (c) Microsoft. All rights reserved.
"""Stock agent for Agent Framework Debug UI."""

import os
from typing import Annotated
from datetime import datetime, timedelta
import random

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential


def get_stock_price(
    symbol: Annotated[str, "The stock symbol to get the price for (e.g., AAPL, MSFT, OPENAI)"],
) -> str:
    """Get the current stock price for a given symbol."""
    # Mock stock data
    stock_data = {
        "AAPL": {"name": "Apple Inc.", "price": 175.43, "change": 2.15, "change_percent": 1.24},
        "MSFT": {"name": "Microsoft Corporation", "price": 378.85, "change": -1.25, "change_percent": -0.33},
        "OPENAI": {"name": "OpenAI", "price": 45.67, "change": 0.89, "change_percent": 1.99},
        "apple": {"name": "Apple Inc.", "price": 175.43, "change": 2.15, "change_percent": 1.24},
        "microsoft": {"name": "Microsoft Corporation", "price": 378.85, "change": -1.25, "change_percent": -0.33},
        "openai": {"name": "OpenAI", "price": 45.67, "change": 0.89, "change_percent": 1.99}
    }
    
    symbol_upper = symbol.upper()
    if symbol_upper in stock_data:
        data = stock_data[symbol_upper]
        change_symbol = "📈" if data["change"] >= 0 else "📉"
        return f"""
📊 **{data['name']} ({symbol_upper})**
💰 **Current Price:** ${data['price']:.2f}
{change_symbol} **Change:** ${data['change']:+.2f} ({data['change_percent']:+.2f}%)
🕐 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    else:
        return f"❌ Stock symbol '{symbol}' not found. Available stocks: AAPL (Apple), MSFT (Microsoft), OPENAI"


def get_stock_analysis(
    symbol: Annotated[str, "The stock symbol to analyze (e.g., AAPL, MSFT, OPENAI)"],
) -> str:
    """Get detailed stock analysis for a given symbol."""
    # Mock analysis data
    analysis_data = {
        "AAPL": {
            "name": "Apple Inc.",
            "rating": "BUY",
            "target_price": 185.00,
            "analysts": 45,
            "recommendation": "Strong Buy",
            "sector": "Technology",
            "market_cap": "2.8T"
        },
        "MSFT": {
            "name": "Microsoft Corporation", 
            "rating": "HOLD",
            "target_price": 385.00,
            "analysts": 38,
            "recommendation": "Hold",
            "sector": "Technology",
            "market_cap": "2.9T"
        },
        "OPENAI": {
            "name": "OpenAI",
            "rating": "BUY", 
            "target_price": 55.00,
            "analysts": 12,
            "recommendation": "Strong Buy",
            "sector": "AI/Technology",
            "market_cap": "90B"
        }
    }
    
    symbol_upper = symbol.upper()
    if symbol_upper in analysis_data:
        data = analysis_data[symbol_upper]
        rating_emoji = "🟢" if data["rating"] == "BUY" else "🟡" if data["rating"] == "HOLD" else "🔴"
        
        return f"""
📈 **{data['name']} Analysis**
{rating_emoji} **Rating:** {data['rating']} - {data['recommendation']}
🎯 **Target Price:** ${data['target_price']:.2f}
👥 **Analysts:** {data['analysts']} covering
🏢 **Sector:** {data['sector']}
💼 **Market Cap:** ${data['market_cap']}
📅 **Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}
        """.strip()
    else:
        return f"❌ Analysis not available for '{symbol}'. Available stocks: AAPL, MSFT, OPENAI"


def get_stock_history(
    symbol: Annotated[str, "The stock symbol to get history for (e.g., AAPL, MSFT, OPENAI)"],
    days: Annotated[int, "Number of days of history to retrieve"] = 7,
) -> str:
    """Get stock price history for a given symbol."""
    # Mock historical data
    stock_names = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation", 
        "OPENAI": "OpenAI"
    }
    
    symbol_upper = symbol.upper()
    if symbol_upper in stock_names:
        base_price = random.uniform(150, 200) if symbol_upper == "AAPL" else random.uniform(350, 400) if symbol_upper == "MSFT" else random.uniform(40, 50)
        
        history = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            price = base_price + random.uniform(-5, 5)
            history.append(f"📅 {date.strftime('%Y-%m-%d')}: ${price:.2f}")
        
        return f"""
📊 **{stock_names[symbol_upper]} ({symbol_upper}) - {days} Day History**
{chr(10).join(history)}
📈 **Trend:** {'Upward' if random.choice([True, False]) else 'Downward'}
        """.strip()
    else:
        return f"❌ History not available for '{symbol}'. Available stocks: AAPL, MSFT, OPENAI"


# Stock agent instance
stock_agent = ChatAgent(
    name="My Stock Agent",
    description="A professional stock market assistant",
    instructions="""
    You are a professional stock market assistant. You can provide:
    - Current stock prices for Apple (AAPL), Microsoft (MSFT), and OpenAI
    - Detailed stock analysis and ratings
    - Historical price data and trends
    
    Always format your responses clearly with emojis and proper structure.
    Be helpful and provide comprehensive stock information when asked.
    """,
    chat_client=AzureOpenAIChatClient(
        endpoint="https://azure-openai-aueast.openai.azure.com/",
        deployment_name="gpt-4o-moretpm",
        credential=AzureCliCredential(),
    ),
    tools=[get_stock_price, get_stock_analysis, get_stock_history],
)

# Export for DevUI
__all__ = ["stock_agent"]
