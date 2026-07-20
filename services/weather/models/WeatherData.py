from dataclasses import dataclass, asdict
from services.weather.models import Current, Daily, HourForecast
from datetime import datetime

@dataclass
class WeatherData:
    observed_at: datetime = None
    current: Current = None
    daily: Daily = None
    hourly: list[HourForecast] = None