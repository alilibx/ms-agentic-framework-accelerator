"""Current weather tool - Get current weather conditions for a location."""

from typing import Annotated
from tools._decorators import tool


@tool(
    domain="weather",
    description="Get current weather conditions for a location",
    tags=["weather", "current", "temperature", "conditions"],
    mock=True,  # This is a mock implementation
)
def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the current weather for a given location.

    This is a mock implementation that returns simulated weather data.
    In production, this would connect to a real weather API.

    Args:
        location: The location to get weather for (e.g., "San Francisco", "New York")

    Returns:
        A formatted string with current weather conditions

    Example:
        >>> get_weather("London")
        "The weather in London is sunny with a high of 22°C."
    """
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 22
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."
