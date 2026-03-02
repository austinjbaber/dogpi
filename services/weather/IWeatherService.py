from abc import ABC, abstractmethod
from services.weather.models import WeatherData

class IWeatherService(ABC):
    '''An interface for weather data. Other modules should depend only on this, not any concrete class that inherits this interface.'''

    @abstractmethod
    def get_weather_data(self) -> WeatherData:
        '''Returns a current snapshot of weather data, including hourly forecast data for the configured location.'''
        pass