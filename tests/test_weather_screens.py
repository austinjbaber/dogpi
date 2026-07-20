"""Regression tests for weather-to-screen conversion and failure handling."""

import importlib
import sys
from datetime import UTC, datetime
from types import ModuleType, SimpleNamespace

import pytest

from services.weather.models import (
    Current,
    Daily,
    HourForecast,
    Temperature,
    WeatherData,
    WindVector,
)


def _empty_weather_state():
    return {
        "fetched_at": None,
        "fetched_ts": 0.0,
        "temp_f": None,
        "feels_f": None,
        "rh": None,
        "wind_mph": None,
        "wind_dir": None,
        "pop": None,
        "hi_f": None,
        "lo_f": None,
        "sunrise": None,
        "sunset": None,
        "hourly": [],
        "err": None,
    }


def _weather_data():
    observed_at = datetime(2026, 1, 15, 14, 5, tzinfo=UTC)
    return WeatherData(
        observed_at=observed_at,
        current=Current(
            temperature=Temperature(72.4),
            apparent_temperature=Temperature(71.6),
            relative_humidity=31,
            wind=WindVector(6.2, 90),
        ),
        daily=Daily(
            high=Temperature(78.2),
            low=Temperature(51.7),
            precipitation_probability=10,
            sunrise=datetime(2026, 1, 15, 7, 25, tzinfo=UTC),
            sunset=datetime(2026, 1, 15, 17, 42, tzinfo=UTC),
        ),
        hourly=[
            HourForecast(
                time=datetime(2026, 1, 15, 15, 0, tzinfo=UTC),
                temperature=Temperature(73.2),
                precipitation_probability=5,
                weather_code=0,
                wmo_abbr="Clear",
                wmo_desc="Clear",
            )
        ],
    )


@pytest.fixture
def screens_module(monkeypatch):
    fake_hardware = ModuleType("hardware")
    fake_hardware.device = SimpleNamespace(size=(128, 64), height=64)
    fake_hardware.SCREEN_FONT = SimpleNamespace(getbbox=lambda _text: (0, 0, 6, 8))
    fake_hardware.WHEN_FONT = fake_hardware.SCREEN_FONT
    monkeypatch.setitem(sys.modules, "hardware", fake_hardware)
    sys.modules.pop("screens", None)

    module = importlib.import_module("screens")
    yield module

    sys.modules.pop("screens", None)


def _stub_weather_dependencies(monkeypatch, screens_module, result):
    monkeypatch.setattr(
        screens_module,
        "Config",
        lambda: SimpleNamespace(base_url="https://example.test", default_headers={}),
    )
    monkeypatch.setattr(screens_module, "HttpService", lambda **_kwargs: object())
    monkeypatch.setattr(
        screens_module,
        "WeatherService",
        lambda **_kwargs: SimpleNamespace(get_weather_data=lambda: result),
    )


def test_process_hourly_forecast_produces_display_values(screens_module):
    hourly = _weather_data().hourly

    result = screens_module.process_hourly_forcast(hourly)

    assert result == [
        {
            "time_str": "3pm",
            "temp_f": 73,
            "pop": 5,
            "code": 0,
            "abbr": "Clear",
            "desc": "Clear",
        }
    ]


def test_weather_refresh_converts_datetimes_and_temperature_objects(
    screens_module, monkeypatch
):
    data = _weather_data()
    _stub_weather_dependencies(monkeypatch, screens_module, data)

    screens_module.weather_refresh()

    assert screens_module.weather["fetched_at"] == "2026-01-15T14:05:00+00:00"
    assert screens_module.weather["fetched_ts"] == data.observed_at.timestamp()
    assert screens_module.weather["sunrise"] == "2026-01-15T07:25:00+00:00"
    assert screens_module.weather["sunset"] == "2026-01-15T17:42:00+00:00"
    assert screens_module.weather["temp_f"] == 72
    assert screens_module.weather["hourly"][0]["temp_f"] == 73
    assert screens_module.weather["err"] is None


def test_weather_refresh_preserves_existing_data_when_no_data_is_available(
    screens_module, monkeypatch
):
    screens_module.weather = _empty_weather_state()
    screens_module.weather["temp_f"] = 72
    existing_weather = screens_module.weather
    _stub_weather_dependencies(monkeypatch, screens_module, None)

    screens_module.weather_refresh()

    assert screens_module.weather is existing_weather
    assert screens_module.weather["temp_f"] == 72
    assert screens_module.weather["err"] == "Weather unavailable"


def test_weather_refresh_preserves_existing_data_when_refresh_raises(
    screens_module, monkeypatch
):
    screens_module.weather = _empty_weather_state()
    screens_module.weather["temp_f"] = 72
    existing_weather = screens_module.weather

    def raise_during_construction(**_kwargs):
        raise RuntimeError("network is down")

    monkeypatch.setattr(
        screens_module,
        "Config",
        lambda: SimpleNamespace(base_url="https://example.test", default_headers={}),
    )
    monkeypatch.setattr(screens_module, "HttpService", lambda **_kwargs: object())
    monkeypatch.setattr(screens_module, "WeatherService", raise_during_construction)

    screens_module.weather_refresh()

    assert screens_module.weather is existing_weather
    assert screens_module.weather["temp_f"] == 72
    assert screens_module.weather["err"] == "network is down"


def test_weather_lines_show_never_before_first_successful_fetch(
    screens_module, monkeypatch
):
    screens_module.weather = _empty_weather_state()
    monkeypatch.setattr(screens_module, "weather_refresh", lambda: None)

    lines = screens_module.weather_lines()

    assert ("--:--  never", "center") in lines
