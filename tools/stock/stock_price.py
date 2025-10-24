"""Stock price tool - Get current stock price and change."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool


@tool(
    domain="stock",
    description="Get current stock price for a symbol",
    tags=["stock", "price", "market", "realtime"],
    mock=True,  # This is a mock implementation
)
def get_stock_price(
    symbol: Annotated[str, "The stock symbol to get the price for (e.g., AAPL, MSFT, OPENAI)"],
) -> str:
    """Get the current stock price for a given symbol.

    This is a mock implementation with sample data.
    In production, this would connect to a real stock market API.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL", "MSFT")

    Returns:
        Formatted string with stock price, change, and timestamp

    Example:
        >>> get_stock_price("AAPL")
        "📊 **Apple Inc. (AAPL)**
        💰 **Current Price:** $175.43
        📈 **Change:** $+2.15 (+1.24%)
        ..."
    """
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
