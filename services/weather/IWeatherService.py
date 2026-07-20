from abc import ABC, abstractmethod
from services.weather.models import WeatherResult

class IWeatherService(ABC):
    '''An interface for weather data. Other modules should depend only on this, not any concrete class that inherits this interface.'''

    @abstractmethod
    def get_weather_data(self) -> WeatherResult:
        '''Returns weather data together with any refresh error or stale-data status.'''
        pass
