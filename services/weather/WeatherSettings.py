from dataclasses import dataclass
from datetime import timedelta
from typing import Mapping


@dataclass(frozen=True)
class WeatherSettings:
    """Configuration required to fetch and interpret weather data."""

    request_parameters: Mapping[str, object]
    refresh_interval: timedelta
    forecast_horizon_hours: int
    wmo_abbr: Mapping[str, str]
    wmo_desc: Mapping[str, str]
