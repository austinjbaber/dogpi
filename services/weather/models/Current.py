from dataclasses import dataclass
from services.weather.models import Temperature, WindVector

@dataclass
class Current:
    temperature: Temperature = None
    apparent_temperature: Temperature = None
    relative_humidity: int = None
    wind: WindVector = None