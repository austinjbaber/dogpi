# DogPi

A Raspberry Pi-powered dog activity logger with a 1.3" OLED display and three-button interface.
Track when your dog pees, poops, or both — with timestamps, a "how long ago" picker, and local weather (plus a short hourly forecast) from Open-Meteo.

## Hardware

| Component | Details |
|---|---|
| Board | Raspberry Pi (any model with GPIO + I2C) |
| Display | 1.3" SH1106 OLED, 128×64, I2C (`0x3C`) |
| Buttons | 3× momentary push-buttons on GPIO 17 (UP), 27 (SEL), 22 (DOWN) |

## Setup

### 1) Enable I2C

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
sudo reboot
```

### 2) Install dependencies

```bash
sudo apt update
sudo apt install -y python3-pip i2c-tools \
  fonts-dejavu fonts-liberation fonts-freefont-ttf

pip3 install -r requirements.txt
```

## Usage

Run from the project directory so `dog_log.json` is found/created in the right place:

```bash
cd dogpi
python3 app.py
```

## UI / Controls

DogPi has 6 modes:

- **Idle**: rain animation + bouncing clock
- **Status**: last pee/poop times + current temperature
- **Menu**: actions (log, undo, weather, forecast)
- **When**: pick how long ago the event happened (hours + 0/15/30/45 minutes)
- **Weather**: current conditions (scrollable)
- **Forecast**: short hourly forecast (scrollable)

### Button controls (UP / SELECT / DOWN)

| Screen | UP | SEL | DOWN |
|---|---|---|---|
| **Idle** | Cycle Background | Wake to Status | Cycle Font |
| **Status** | — | Open Menu | — |
| **Menu** | Scroll Up | Choose | Scroll Down|
| **When** | Increment | Next / Confirm | Decrement |
| **Weather** | Scroll Up | — | Scroll Down |
| **Forecast** | Scroll Up | — | Scroll Down |

**Hold SELECT (0.6s)** for “back/cancel”:

- Status → Idle
- Menu → Status
- When → Cancel log (back to Status)
- Weather / Forecast → Back to Menu

Display returns to **Idle** after 25s of inactivity

## Idle Animation Timing

Idle animation uses a single timing convention across all files in `idle/`:

- Motion updates use real elapsed time in seconds (`dt`).
- Speed constants are expressed in per-second units.
- Frame pacing is separate from motion math and is capped at **40 FPS** by default.

Tune idle pacing in `idle/__init__.py`:

- `IDLE_TARGET_FPS = 40.0`

For SH1106 over I2C, a practical range is usually **24-40 FPS** depending on smoothness vs CPU/I2C load.

## Weather

Weather data is fetched from Open-Meteo (no API key required).
Default coordinates are Tucson, AZ. Weather options are configured in `config.json`:

- `request_parameters.latitude` / `request_parameters.longitude`: forecast location
- `refresh_interval_seconds`: minimum time between refresh attempts (default: 600 seconds)
- `forecast_horizon_hours`: number of upcoming hourly entries to keep (default: 24)
- `request_parameters`: Open-Meteo units and requested current, daily, and hourly fields

Behavior:

- `app.py` constructs one `HttpService` and `WeatherService`, then injects the weather service into `screens.py`.
- Refresh attempts occur at most once per configured refresh interval, including after failures.
- If a refresh fails, the most recent successful data remains available and is reported as stale with an error.
- The status screen shows the current Open-Meteo temperature when available.
- The forecast displays compact hourly time, temperature, precipitation, and WMO condition values.

## Tests

Run the complete test suite from the project directory:

```bash
python3 -m pytest -q
```

Tests cover time and direction helpers, HTTP transport failures, weather parsing and caching, refresh throttling, stale-data fallback, timezone handling, and weather screen conversion.

## Data

Events are stored in `dog_log.json` as a flat list:

```json
{
  "events": [
    {"type": "dog", "value": "pee",  "ts": "2026-02-18T14:30:00"},
    {"type": "dog", "value": "both", "ts": "2026-02-18T08:15:00"}
  ]
}
```

## Project structure

```
dogpi/
├── app.py                     Composition root and main display loop
├── config.py                  JSON-backed application configuration
├── config.json                Weather location, fields, units, and timing
├── hardware.py                GPIO buttons, SH1106 device setup, shared fonts
├── inputs.py                  Button callbacks and input wiring
├── screens.py                 UI state, weather view models, and rendering
├── state.py                   Event persistence and lookup helpers
├── helpers/                   Time, direction, and number helpers
├── idle/                      Idle renderer and animated backgrounds
├── services/
│   ├── http/
│   │   ├── IHttpService.py    HTTP abstraction
│   │   ├── HttpService.py     urllib-based HTTP implementation
│   │   └── models/            HttpResponse model
│   └── weather/
│       ├── IWeatherService.py Weather abstraction consumed by screens
│       ├── WeatherService.py  Open-Meteo adapter, parser, and cache
│       ├── WeatherSettings.py Injected weather configuration
│       └── models/            Current, daily, hourly, and result models
├── tests/
│   ├── test_http_service.py
│   ├── test_weather_service.py
│   ├── test_weather_screens.py
│   ├── test_time_helpers.py
│   └── test_direction_helpers.py
└── dog_log.json               Event log (created automatically)
```

### Module dependency graph

```
app.py
 ├── config
 ├── hardware
 ├── services
 │    ├── http
 │    └── weather
 │         └── helpers
 ├── screens
 │    ├── IWeatherService
 │    ├── hardware
 │    ├── helpers
 │    └── state
 ├── idle
 │    └── hardware
 └── inputs
      ├── hardware
      ├── idle
      └── screens
```

`app.py` is the composition root: it creates the concrete HTTP and weather services and configures `screens.py` through `IWeatherService` before input callbacks are registered.
