#!/usr/bin/env python3
"""DogPi — dog activity logger with OLED UI on Raspberry Pi."""

import time
from datetime import timedelta

from config import Config
from hardware import BTN_UP, BTN_DOWN, BTN_SEL, SCREEN_FONT, WHEN_FONT, TOAST_FONT
from services import HttpService, WeatherService, WeatherSettings
import screens
from screens import (
    ui, render_lines,
    MODE_IDLE, MODE_STATUS, MODE_MENU, MODE_WHEN, MODE_WEATHER, MODE_FORECAST,
    IDLE_TIMEOUT_S,
    status_lines, menu_lines, when_lines, weather_lines, forecast_lines,
)
from idle import render_idle_frame

config = Config()
http_service = HttpService(
    base_url=config.base_url,
    default_headers=config.default_headers,
)
weather_settings = WeatherSettings(
    request_parameters=config.request_parameters,
    refresh_interval=timedelta(seconds=config.refresh_interval_seconds),
    forecast_horizon_hours=config.forecast_horizon_hours,
    wmo_abbr=config.wmo_abbr,
    wmo_desc=config.wmo_desc,
)
weather_service = WeatherService(
    http_service=http_service,
    settings=weather_settings,
)
screens.configure_weather_service(weather_service)

import inputs  # noqa: F401 — wires button callbacks on import

# ----------------------------
# Main loop
# ----------------------------
print("DogPi running. Ctrl+C to exit.")
#print(device.size)
try:
    while True:
        # Idle timeout (don't idle while a toast is showing)
        if not (ui.toast_lines and time.time() < ui.toast_until):
            if ui.mode != MODE_IDLE:
                if (time.monotonic() - ui.last_input_t) > IDLE_TIMEOUT_S:
                    ui.mode = MODE_IDLE

        # Toast takes priority
        if ui.toast_lines and time.time() < ui.toast_until:
            render_lines(ui.toast_lines, font=TOAST_FONT)
            time.sleep(0.05)
            continue
        else:
            ui.toast_lines = None

        if ui.mode == MODE_IDLE:
            render_idle_frame()
            # no sleep for smoother animation
        elif ui.mode == MODE_STATUS:
            render_lines(status_lines(), font=SCREEN_FONT)
            time.sleep(0.10)
        elif ui.mode == MODE_WEATHER:
            lines = weather_lines()
            render_lines(lines[ui.weather_scroll:], font=SCREEN_FONT)
            time.sleep(0.10)
        elif ui.mode == MODE_FORECAST:
            lines = forecast_lines()
            render_lines(lines[ui.forecast_scroll:], font=SCREEN_FONT)
            time.sleep(0.10)
        elif ui.mode == MODE_MENU:
            render_lines(menu_lines(), font=SCREEN_FONT)
            time.sleep(0.10)
        elif ui.mode == MODE_WHEN:
            render_lines(when_lines(), font=WHEN_FONT)
            time.sleep(0.10)

except KeyboardInterrupt:
    pass
finally:
    try:
        BTN_UP.close()
        BTN_DOWN.close()
        BTN_SEL.close()
    except Exception:
        pass
