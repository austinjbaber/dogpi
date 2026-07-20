from services.http import IHttpService, HttpResponse
from services.weather.IWeatherService import IWeatherService
from services.weather.WeatherServiceError import WeatherServiceError
from services.weather.WeatherSettings import WeatherSettings
from services.weather.models import WeatherData, WeatherResult, Temperature, WindVector, HourForecast, Current, Daily
from collections.abc import Callable
from datetime import datetime, UTC
from zoneinfo import ZoneInfo


def _utc_now() -> datetime:
    return datetime.now(UTC)


class WeatherService(IWeatherService):
    def __init__(
        self,
        http_service: IHttpService,
        settings: WeatherSettings,
        clock: Callable[[], datetime] = _utc_now,
    ):
        self.http_svc: IHttpService = http_service
        self.settings = settings
        self.clock = clock
        self.request_parameters = settings.request_parameters
        self.refresh_interval = settings.refresh_interval
        self.forecast_horizon_hours = settings.forecast_horizon_hours
        self.weather_dict: dict | None = None
        self.weather_data: WeatherData | None = None
        self.last_update: datetime | None = None
        self.last_attempt: datetime | None = None
        self.last_error: str | None = None
        self.time_zone: ZoneInfo | None = None

    def _fetch_openmeteo_data(self) -> None:
        params: dict = dict(self.request_parameters)
        for key in ("current", "daily", "hourly"):
            value = params.get(key)
            if isinstance(value, list):
                params[key] = ",".join(value)

        response: HttpResponse = self.http_svc.get("/forecast", params=params)
        if response.status_code != 200:
            raise WeatherServiceError(
                f"Weather request failed with HTTP {response.status_code}"
            )

        weather_dict = response.body_to_json_object()
        if not isinstance(weather_dict, dict):
            raise WeatherServiceError("Weather response did not contain JSON data")

        timezone_name = weather_dict.get("timezone")
        if not timezone_name:
            raise WeatherServiceError("Weather response did not include a timezone")

        time_zone = ZoneInfo(timezone_name)
        self.weather_dict = weather_dict
        self.time_zone = time_zone
    
    def _can_update_data(self) -> bool:
        if not self.last_attempt:
            return True
        
        next_update = self.last_attempt + self.refresh_interval
        return self.clock() > next_update
    
    def _get_current_values(self, data: WeatherData) -> bool:
        current: dict = self.weather_dict.get("current", {})
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
        daily: dict = self.weather_dict.get("daily")
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
        hourly: dict = self.weather_dict.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        pops  = hourly.get("precipitation_probability", [])
        codes = hourly.get("weather_code", [])

        
        now = self.clock().astimezone(self.time_zone)
        start_index = next(
            (
                idx
                for idx, time in enumerate(times)
                if datetime.fromisoformat(time).replace(tzinfo=self.time_zone) > now
            ),
            -1,
        )
        if start_index == -1:
            return
        
        for idx in range(start_index, min(start_index + self.forecast_horizon_hours, len(times))):
            hourly_forecast = HourForecast()
            hourly_forecast.time = datetime.fromisoformat(times[idx]).replace(tzinfo=self.time_zone)
            hourly_forecast.temperature = Temperature(
                temps[idx]
            )
            hourly_forecast.precipitation_probability = pops[idx]
            hourly_forecast.weather_code = codes[idx]
            hourly_forecast.wmo_abbr = self.settings.wmo_abbr[str(codes[idx])]
            hourly_forecast.wmo_desc = self.settings.wmo_desc[str(codes[idx])]
            data.hourly.append(hourly_forecast)

    def get_weather_data(self) -> WeatherResult:
        if not self._can_update_data():
            return WeatherResult(
                data=self.weather_data,
                error=self.last_error,
                is_stale=self.last_error is not None and self.weather_data is not None,
            )

        self.last_attempt = self.clock()
        try:
            self._fetch_openmeteo_data()
            weather_data = WeatherData()
            weather_data.observed_at = datetime.fromisoformat(self.weather_dict.get("current").get("time")).replace(tzinfo=self.time_zone)
            self._get_current_values(weather_data)
            self._get_daily_values(weather_data)
            self._get_hourly_values(weather_data)
            self.weather_data = weather_data
            self.last_update = self.last_attempt
            self.last_error = None
            return WeatherResult(data=self.weather_data)
        except Exception as exc:
            self.last_error = str(exc) or type(exc).__name__
            return WeatherResult(
                data=self.weather_data,
                error=self.last_error,
                is_stale=self.weather_data is not None,
            )
