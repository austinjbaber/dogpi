"""Regression tests for the current WeatherService fixes."""

import copy
import importlib
import json
from datetime import UTC, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from services.http.models import HttpResponse
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
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, relative_url, headers=None, params=None):
        self.calls.append(
            {
                "relative_url": relative_url,
                "headers": headers,
                "params": copy.deepcopy(params),
            }
        )
        return HttpResponse(
            status_code=200,
            headers={},
            body=json.dumps(self.payload).encode("utf-8"),
        )


@pytest.fixture(autouse=True)
def reset_weather_service_singleton():
    WeatherService._instance = None
    yield
    WeatherService._instance = None


@pytest.fixture
def fake_config(monkeypatch):
    config = SimpleNamespace(
        request_parameters={
            "latitude": "32.2226",
            "longitude": "-110.9747",
            "current": ["temperature_2m", "apparent_temperature"],
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "hourly": ["temperature_2m", "weather_code"],
        },
        refresh_interval_seconds=600,
        forcast_horizon_hours=24,
        wmo_abbr={"0": "Clear"},
        wmo_desc={"0": "Clear"},
    )
    monkeypatch.setattr(weather_service_module, "Config", lambda: config)
    monkeypatch.setattr(weather_service_module, "ZoneInfo", lambda _name: UTC)
    return config


def test_constructor_accepts_injected_http_service_keyword(fake_config):
    http_service = FakeHttpService(_weather_payload())

    service = WeatherService(http_service=http_service)

    assert service.http_svc is http_service


def test_fetch_formats_a_copy_without_mutating_request_parameters(fake_config):
    original_parameters = copy.deepcopy(fake_config.request_parameters)
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(http_service=http_service)

    assert service._fetch_openmeteo_data() is True
    assert service._fetch_openmeteo_data() is True

    assert fake_config.request_parameters == original_parameters
    assert http_service.calls[0]["params"]["current"] == (
        "temperature_2m,apparent_temperature"
    )
    assert http_service.calls[1]["params"] == http_service.calls[0]["params"]


def test_second_get_within_refresh_interval_returns_cached_data(fake_config):
    http_service = FakeHttpService(_weather_payload())
    service = WeatherService(http_service=http_service)

    first_result = service.get_weather_data()
    second_result = service.get_weather_data()

    assert isinstance(service.last_update, datetime)
    assert second_result is first_result
    assert len(http_service.calls) == 1


def test_hourly_times_are_interpreted_in_the_api_timezone(fake_config, monkeypatch):
    fixed_instant = datetime(2026, 1, 15, 3, 30, tzinfo=UTC)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return fixed_instant.replace(tzinfo=None)
            return fixed_instant.astimezone(tz)

    monkeypatch.setattr(weather_service_module, "datetime", FixedDateTime)

    api_timezone = timezone(timedelta(hours=9), name="Asia/Tokyo")
    service = WeatherService(http_service=FakeHttpService(_weather_payload()))
    service.time_zone = api_timezone
    service.weather_dict = _weather_payload(
        timezone="Asia/Tokyo",
        hourly_times=["2026-01-15T12:00", "2026-01-15T13:00"],
    )
    data = WeatherData()

    service._get_hourly_values(data)

    assert data.hourly[0].time.hour == 13
    assert data.hourly[0].time.tzinfo is api_timezone
