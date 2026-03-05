from dataclasses import dataclass
from services.weather.models import Temperature
from datetime import datetime

@dataclass
class HourForecast:
    time: datetime = None
    temperature: Temperature = None
    precipitation_probability: int = None
    weather_code: int = None
    wmo_abbr: str = None
    wmo_desc: str = None