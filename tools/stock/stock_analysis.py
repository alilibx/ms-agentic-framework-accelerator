"""Stock analysis tool - Get detailed stock analysis and ratings."""

from typing import Annotated
from datetime import datetime
from tools._decorators import tool


@tool(
    domain="stock",
    description="Get detailed stock analysis and analyst ratings",
    tags=["stock", "analysis", "rating", "recommendation"],
    mock=True,  # This is a mock implementation
)
def get_stock_analysis(
    symbol: Annotated[str, "The stock symbol to analyze (e.g., AAPL, MSFT, OPENAI)"],
) -> str:
    """Get detailed stock analysis for a given symbol.

    This is a mock implementation with sample analysis data.
    In production, this would connect to financial analysis APIs.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Formatted string with analyst ratings, target price, and recommendations

    Example:
        >>> get_stock_analysis("AAPL")
        "📈 **Apple Inc. Analysis**
        🟢 **Rating:** BUY - Strong Buy
        🎯 **Target Price:** $185.00
        ..."
    """
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
