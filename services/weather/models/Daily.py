from dataclasses import dataclass
from services.weather.models import Temperature
from datetime import datetime

@dataclass
class Daily:
    high: Temperature = None
    low: Temperature = None
    precipitation_probability: int = None
    sunrise: datetime = None
    sunset: datetime = None