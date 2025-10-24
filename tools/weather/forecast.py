"""Weather forecast tool - Get multi-day weather forecast."""

from typing import Annotated
from tools._decorators import tool


@tool(
    domain="weather",
    description="Get weather forecast for multiple days",
    tags=["weather", "forecast", "multi-day", "prediction"],
    mock=True,  # This is a mock implementation
)
def get_forecast(
    location: Annotated[str, "The location to get the forecast for."],
    days: Annotated[int, "Number of days for forecast"] = 3,
) -> str:
    """Get weather forecast for multiple days.

    This is a mock implementation that returns simulated forecast data.
    In production, this would connect to a real weather API.

    Args:
        location: The location to get forecast for
        days: Number of days to forecast (default: 3, max: 7)

    Returns:
        A formatted string with multi-day weather forecast

    Example:
        >>> get_forecast("Paris", days=5)
        "Weather forecast for Paris:
        Day 1: cloudy, 19°C
        Day 2: rainy, 20°C
        ..."
    """
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    forecast: list[str] = []

    for day in range(1, days + 1):
        condition = conditions[day % len(conditions)]
        temp = 18 + day
        forecast.append(f"Day {day}: {condition}, {temp}°C")

    return f"Weather forecast for {location}:\n" + "\n".join(forecast)
