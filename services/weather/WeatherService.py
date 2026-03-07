from services.http import IHttpService, HttpResponse
from services.weather.IWeatherService import IWeatherService
from services.weather.models import WeatherData, Temperature, WindVector, HourForecast, Current, Daily
from config import Config
from datetime import datetime, UTC, timedelta
from zoneinfo import ZoneInfo

class WeatherService(IWeatherService):
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, http_service: IHttpService):
        if hasattr(self, "initialized"):
            return
        self.http_svc: IHttpService = http_service
        self.config: Config = Config()
        self.request_parameters = self.config.request_parameters
        self.refresh_interval_seconds: timedelta = timedelta(seconds=self.config.refresh_interval_seconds)
        self.forcast_horizon_hours = self.config.forcast_horizon_hours
        self.weather: dict = None
        self.last_update: datetime = None
        self.time_zone: ZoneInfo = None
        self.initialized: bool = True

    def _fetch_openmeteo_data(self) -> bool:
        params:dict = self.request_parameters
        params["current"] = ",".join(params.get("current", ""))
        params["daily"] = ",".join(params.get("daily", ""))
        params["hourly"] = ",".join(params.get("hourly", ""))

        try:
            response: HttpResponse = self.http_svc.get("/forecast", params=params)
            if not response.status_code == 200:
                return False
            
            self.weather = response.body_to_json_object()
            self.last_update = datetime.now(UTC).isoformat(timespec="seconds")
            self.time_zone = ZoneInfo(self.weather.get("timezone"))
            return True
        except Exception as e:
            # Log exceptions here
            print(f"Error: {repr(e)}")
            return False
    
    def _can_update_data(self) -> bool:
        if not self.last_update:
            return True
        
        next_update = self.last_update + self.refresh_interval_seconds
        return datetime.now(UTC) > next_update
    
    def _get_current_values(self, data: WeatherData) -> bool:
        current: dict = self.weather.get("current", {})
        data.current = Current()
        data.current.temperature = Temperature(
            current.get("temperature_2m")
        )
        data.current.apparent_temperature = Temperature(
            current.get("apparent_temperature")
        )
        data.current.relative_humidity = current.get("relative_humidity_2m")
        data.current.wind= WindVector(
            current.get("wind_speed_10m"),
            current.get("wind_direction_10m")
        )
    
    def _get_daily_values(self, data: WeatherData):
        daily: dict = self.weather.get("daily")
        data.daily = Daily()
        data.daily.precipitation_probability = daily.get("precipitation_probability_max")[0]
        data.daily.high = Temperature(
            daily.get("temperature_2m_max")[0]
        )
        data.daily.low = Temperature(
            daily.get("temperature_2m_min")[0]
        )
        data.daily.sunrise = datetime.fromisoformat(daily.get("sunrise")[0]).replace(tzinfo=self.time_zone)
        data.daily.sunset = datetime.fromisoformat(daily.get("sunset")[0]).replace(tzinfo=self.time_zone)

    def _get_hourly_values(self, data: WeatherData):
        data.hourly = []
        hourly: dict = self.weather.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        pops  = hourly.get("precipitation_probability", [])
        codes = hourly.get("weather_code", [])

        
        now = datetime.now(self.time_zone)
        start_index = next((idx for idx, time in enumerate(times) if datetime.fromisoformat(time).astimezone(self.time_zone) > now), -1)
        if start_index == -1:
            return
        
        for idx in range(start_index, min(start_index + self.forcast_horizon_hours, len(times))):
            hourly_forecast = HourForecast()
            hourly_forecast.time = datetime.fromisoformat(times[idx]).replace(tzinfo=self.time_zone)
            hourly_forecast.temperature = Temperature(
                temps[idx]
            )
            hourly_forecast.precipitation_probability = pops[idx]
            hourly_forecast.weather_code = codes[idx]
            hourly_forecast.wmo_abbr = self.config.wmo_abbr[str(codes[idx])]
            hourly_forecast.wmo_desc = self.config.wmo_desc[str(codes[idx])]
            data.hourly.append(hourly_forecast)

    def get_weather_data(self) -> WeatherData | None:
        if self._can_update_data() and self._fetch_openmeteo_data():
            weather_data = WeatherData()
            weather_data.observed_at = datetime.fromisoformat(self.weather.get("current").get("time")).replace(tzinfo=self.time_zone)
            self._get_current_values(weather_data)
            self._get_daily_values(weather_data)
            self._get_hourly_values(weather_data)
            return weather_data
        
        return None