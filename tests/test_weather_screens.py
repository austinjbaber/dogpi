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
    WeatherResult,
    WindVector,
)


def _empty_weather_state(screens_module):
    return screens_module.WeatherViewState()


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


def _configure_weather_result(
    screens_module,
    data,
    error=None,
    is_stale=False,
):
    screens_module.configure_weather_service(
        SimpleNamespace(
            get_weather_data=lambda: WeatherResult(
                data=data,
                error=error,
                is_stale=is_stale,
            )
        )
    )


def test_process_hourly_forecast_produces_display_values(screens_module):
    hourly = _weather_data().hourly

    result = screens_module.process_hourly_forecast(hourly)

    assert result == [
        screens_module.HourlyWeatherView(
            time_str="3pm",
            temp_f=73,
            pop=5,
            code=0,
            abbr="Clear",
            desc="Clear",
        )
    ]


def test_weather_view_states_do_not_share_hourly_lists(screens_module):
    first = screens_module.WeatherViewState()
    second = screens_module.WeatherViewState()

    first.hourly.append(screens_module.HourlyWeatherView())

    assert second.hourly == []


def test_weather_refresh_converts_datetimes_and_temperature_objects(screens_module):
    data = _weather_data()
    _configure_weather_result(screens_module, data)

    screens_module.weather_refresh()

    assert screens_module.weather.fetched_at == "2026-01-15T14:05:00+00:00"
    assert screens_module.weather.fetched_ts == data.observed_at.timestamp()
    assert screens_module.weather.sunrise == "2026-01-15T07:25:00+00:00"
    assert screens_module.weather.sunset == "2026-01-15T17:42:00+00:00"
    assert screens_module.weather.temp_f == 72
    assert screens_module.weather.hourly[0].temp_f == 73
    assert screens_module.weather.err is None
    assert screens_module.weather.is_stale is False


def test_weather_refresh_preserves_existing_data_when_no_data_is_available(
    screens_module,
):
    screens_module.weather = _empty_weather_state(screens_module)
    screens_module.weather.temp_f = 72
    existing_weather = screens_module.weather
    _configure_weather_result(screens_module, None, error="Weather unavailable")

    screens_module.weather_refresh()

    assert screens_module.weather is existing_weather
    assert screens_module.weather.temp_f == 72
    assert screens_module.weather.err == "Weather unavailable"


def test_weather_refresh_displays_an_error_with_stale_data(screens_module):
    data = _weather_data()
    _configure_weather_result(
        screens_module,
        data,
        error="network is down",
        is_stale=True,
    )

    screens_module.weather_refresh()

    assert screens_module.weather.temp_f == 72
    assert screens_module.weather.err == "network is down"
    assert screens_module.weather.is_stale is True


def test_weather_refresh_preserves_existing_data_when_refresh_raises(screens_module):
    screens_module.weather = _empty_weather_state(screens_module)
    screens_module.weather.temp_f = 72
    existing_weather = screens_module.weather

    def raise_during_refresh():
        raise RuntimeError("network is down")

    screens_module.configure_weather_service(
        SimpleNamespace(get_weather_data=raise_during_refresh)
    )

    screens_module.weather_refresh()

    assert screens_module.weather is existing_weather
    assert screens_module.weather.temp_f == 72
    assert screens_module.weather.err == "network is down"


def test_weather_refresh_reuses_the_configured_service(screens_module):
    data = _weather_data()
    calls = []

    def get_weather_data():
        calls.append(True)
        return WeatherResult(data=data)

    service = SimpleNamespace(get_weather_data=get_weather_data)
    screens_module.configure_weather_service(service)

    screens_module.weather_refresh()
    screens_module.weather_refresh()

    assert screens_module._weather_service is service
    assert len(calls) == 2


def test_weather_lines_show_never_before_first_successful_fetch(
    screens_module, monkeypatch
):
    screens_module.weather = _empty_weather_state(screens_module)
    monkeypatch.setattr(screens_module, "weather_refresh", lambda: None)

    lines = screens_module.weather_lines()

    assert ("--:--  never", "center") in lines
