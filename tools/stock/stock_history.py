"""Stock history tool - Get historical price data."""

from typing import Annotated
from datetime import datetime, timedelta
import random
from tools._decorators import tool


@tool(
    domain="stock",
    description="Get historical stock price data",
    tags=["stock", "history", "historical", "trend"],
    mock=True,  # This is a mock implementation
)
def get_stock_history(
    symbol: Annotated[str, "The stock symbol to get history for (e.g., AAPL, MSFT, OPENAI)"],
    days: Annotated[int, "Number of days of history to retrieve"] = 7,
) -> str:
    """Get stock price history for a given symbol.

    This is a mock implementation with randomly generated historical data.
    In production, this would fetch real historical market data.

    Args:
        symbol: Stock ticker symbol
        days: Number of days of history (default: 7, max: 365)

    Returns:
        Formatted string with daily price history and trend

    Example:
        >>> get_stock_history("AAPL", days=5)
        "📊 **Apple Inc. (AAPL) - 5 Day History**
        📅 2025-10-24: $176.23
        📅 2025-10-23: $175.12
        ..."
    """
    # Mock historical data
    stock_names = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "OPENAI": "OpenAI"
    }

    symbol_upper = symbol.upper()
    if symbol_upper in stock_names:
        base_price = (
            random.uniform(150, 200) if symbol_upper == "AAPL"
            else random.uniform(350, 400) if symbol_upper == "MSFT"
            else random.uniform(40, 50)
        )

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
