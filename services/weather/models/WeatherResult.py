from dataclasses import dataclass

from services.weather.models.WeatherData import WeatherData


@dataclass(frozen=True)
class WeatherResult:
    """Outcome of a weather lookup, optionally containing stale cached data."""

    data: WeatherData | None
    error: str | None = None
    is_stale: bool = False
