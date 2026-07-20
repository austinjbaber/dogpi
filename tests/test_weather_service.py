"""Regression tests for the current WeatherService fixes."""

import copy
import importlib
import json
from datetime import UTC, datetime, timedelta, timezone

import pytest

from services.http.models import HttpResponse
from services.http import HttpTransportError
from services.weather.WeatherSettings import WeatherSettings
from services.weather.models import WeatherData


weather_service_module = importlib.import_module("services.weather.WeatherService")
WeatherService = weather_service_module.WeatherService


def _weather_payload(*, timezone="UTC", hourly_times=None):
    hourly_times = hourly_times or []
    return {
        "timezone": timezone,
        "current": {
            "time": "2026-01-15T12:00",
            "temperature_2m": 72.4,
            "apparent_temperature": 71.6,
            "relative_humidity_2m": 31,
            "wind_speed_10m": 6.2,
            "wind_direction_10m": 90,
        },
        "daily": {
            "precipitation_probability_max": [10],
            "temperature_2m_max": [78.2],
            "temperature_2m_min": [51.7],
            "sunrise": ["2026-01-15T07:25"],
            "sunset": ["2026-01-15T17:42"],
        },
        "hourly": {
            "time": hourly_times,
            "temperature_2m": [70.0 + index for index in range(len(hourly_times))],
            "precipitation_probability": [5 for _ in hourly_times],
            "weather_code": [0 for _ in hourly_times],
        },
    }


class FakeHttpService:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.error = None
        self.calls = []

    def get(self, relative_url, headers=None, params=None):
        self.calls.append(
            {
                "relative_url": relative_url,
                "headers": headers,
                "params": copy.deepcopy(params),
            }
        )
        if self.error:
            raise self.error
        return HttpResponse(
            status_code=self.status_code,
            headers={},
            body=json.dumps(self.payload).encode("utf-8"),
        )


@pytest.fixture
def weather_settings(monkeypatch):
    settings = WeatherSettings(
        request_parameters={
            "latitude": "32.2226",
            "longitude": "-110.9747",
            "current": ["temperature_2m", "apparent_temperature"],
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "hourly": ["temperature_2m", "weather_code"],
        },
        refresh_interval=timedelta(seconds=600),
        forecast_horizon_hours=24,
        wmo_abbr={"0": "Clear"},
        wmo_desc={"0": "Clear"},
    )
    monkeypatch.setattr(weather_service_module, "ZoneInfo", lambda _name: UTC)
    return settings


def test_each_service_instance_keeps_its_injected_dependencies(weather_settings):
    first_http_service = FakeHttpService(_weather_payload())
    second_http_service = FakeHttpService(_weather_payload())

    first_service = WeatherService(
        http_service=first_http_service,
        settings=weather_settings,
    )
    second_service = WeatherService(
        http_service=second_http_service,
        settings=weather_settings,
    )

    assert first_service is not second_service
    assert first_service.http_svc is first_http_service
    assert second_service.http_svc is second_http_service
    assert first_service.settings is weather_settings


def test_fetch_formats_a_copy_without_mutating_request_parameters(weather_settings):
    original_parameters = copy.deepcopy(weather_settings.request_parameters)
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(http_service=http_service, settings=weather_settings)

    assert service._fetch_openmeteo_data() is None
    assert service._fetch_openmeteo_data() is None

    assert weather_settings.request_parameters == original_parameters
    assert http_service.calls[0]["params"]["current"] == (
        "temperature_2m,apparent_temperature"
    )
    assert http_service.calls[1]["params"] == http_service.calls[0]["params"]


def test_second_get_within_refresh_interval_returns_cached_data(weather_settings):
    fixed_instant = datetime(2026, 1, 15, 3, 30, tzinfo=UTC)
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(
        http_service=http_service,
        settings=weather_settings,
        clock=lambda: fixed_instant,
    )

    first_result = service.get_weather_data()
    second_result = service.get_weather_data()

    assert isinstance(service.last_update, datetime)
    assert first_result.error is None
    assert second_result.error is None
    assert second_result.data is first_result.data
    assert len(http_service.calls) == 1


def test_refreshes_after_the_injected_clock_passes_the_interval(weather_settings):
    current_time = [datetime(2026, 1, 15, 3, 30, tzinfo=UTC)]
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(
        http_service=http_service,
        settings=weather_settings,
        clock=lambda: current_time[0],
    )

    first_result = service.get_weather_data()
    current_time[0] += timedelta(minutes=11)
    second_result = service.get_weather_data()

    assert second_result.data is not first_result.data
    assert len(http_service.calls) == 2


def test_initial_transport_failure_returns_an_explicit_error(weather_settings):
    http_service = FakeHttpService(_weather_payload())
    http_service.error = HttpTransportError("network is down")
    fixed_instant = datetime(2026, 1, 15, 3, 30, tzinfo=UTC)
    service = WeatherService(
        http_service=http_service,
        settings=weather_settings,
        clock=lambda: fixed_instant,
    )

    result = service.get_weather_data()
    repeated_result = service.get_weather_data()

    assert result.data is None
    assert result.error == "network is down"
    assert result.is_stale is False
    assert repeated_result.error == "network is down"
    assert len(http_service.calls) == 1


def test_failed_refresh_returns_cached_data_marked_stale(weather_settings):
    current_time = [datetime(2026, 1, 15, 3, 30, tzinfo=UTC)]
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(
        http_service=http_service,
        settings=weather_settings,
        clock=lambda: current_time[0],
    )
    successful_result = service.get_weather_data()
    current_time[0] += timedelta(minutes=11)
    http_service.error = HttpTransportError("network is down")

    failed_result = service.get_weather_data()
    repeated_result = service.get_weather_data()

    assert failed_result.data is successful_result.data
    assert failed_result.error == "network is down"
    assert failed_result.is_stale is True
    assert repeated_result.data is successful_result.data
    assert repeated_result.error == "network is down"
    assert repeated_result.is_stale is True
    assert len(http_service.calls) == 2


def test_malformed_refresh_does_not_replace_cached_data(weather_settings):
    current_time = [datetime(2026, 1, 15, 3, 30, tzinfo=UTC)]
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(
        http_service=http_service,
        settings=weather_settings,
        clock=lambda: current_time[0],
    )
    successful_result = service.get_weather_data()
    current_time[0] += timedelta(minutes=11)
    malformed_payload = _weather_payload()
    malformed_payload["daily"] = {}
    http_service.payload = malformed_payload

    failed_result = service.get_weather_data()

    assert failed_result.data is successful_result.data
    assert failed_result.error is not None
    assert failed_result.is_stale is True


def test_non_success_response_returns_an_explicit_error(weather_settings):
    http_service = FakeHttpService(_weather_payload(), status_code=503)
    service = WeatherService(http_service=http_service, settings=weather_settings)

    result = service.get_weather_data()

    assert result.data is None
    assert result.error == "Weather request failed with HTTP 503"
    assert result.is_stale is False


def test_hourly_times_are_interpreted_in_the_api_timezone(weather_settings):
    fixed_instant = datetime(2026, 1, 15, 3, 30, tzinfo=UTC)

    api_timezone = timezone(timedelta(hours=9), name="Asia/Tokyo")
    service = WeatherService(
        http_service=FakeHttpService(_weather_payload()),
        settings=weather_settings,
        clock=lambda: fixed_instant,
    )
    service.time_zone = api_timezone
    service.weather_dict = _weather_payload(
        timezone="Asia/Tokyo",
        hourly_times=["2026-01-15T12:00", "2026-01-15T13:00"],
    )
    data = WeatherData()

    service._get_hourly_values(data)

    assert data.hourly[0].time.hour == 13
    assert data.hourly[0].time.tzinfo is api_timezone
