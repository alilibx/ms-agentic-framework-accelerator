"""Weather domain tools.

This package contains all weather-related tools that can be discovered
and used by agents.
"""

from tools.weather.current_weather import get_weather
from tools.weather.forecast import get_forecast

__all__ = ["get_weather", "get_forecast"]
