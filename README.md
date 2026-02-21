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

pip3 install gpiozero luma.oled Pillow
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

### Button controls (UP--SELECT--DOWN)

| Screen | UP | SEL | DOWN |
|---|---|---|---|
| **Idle** | Wake to Status | Wake to Status | Wake to Status |
| **Status** | — | Open Menu | — |
| **Menu** | Scroll Up | Choose | Scroll Down|
| **When** | Increment | Next/ Confirm | Decrement |
| **Weather** | Scroll Up | — | Scroll Down |
| **Forecast** | Scroll Up | — | Scroll Dowm |

**Hold SEL (0.6s)** for “back/cancel” shortcuts:

- Status → Idle
- Menu → Status
- When → Cancel log (back to Status)
- Weather / Forecast → Back to Menu

Display returns to **Idle** after 25s of inactivity

## Weather

Weather data is fetched from Open-Meteo (no API key required).
Default coordinates are Tucson, AZ — edit `WEATHER_LAT` / `WEATHER_LON` in `weather.py` to change location.

Behavior:

- Refreshes at most every **10 minutes** (`WEATHER_REFRESH_S`)
- Shows cached data for up to **2 hours** (`WEATHER_MAX_STALE_S`)
- Status screen shows **ambient temp** from Open-Meteo when available; otherwise falls back to **CPU temp**
- Forecast keeps the next **12 hours** (`HOURLY_HOURS`) and displays a compact WMO condition abbreviation

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
├── app.py           Main loop — imports everything, runs the UI
├── hardware.py      Buttons, OLED device, font loading
├── state.py         JSON persistence (dog_log.json) and event helpers
├── helpers.py       Stateless time-formatting utilities
├── weather.py       Open-Meteo API fetch, caching, temperature + hourly forecast
├── screens.py       Shared UI state, rendering, screen content builders
├── idle.py          Rain + DVD-bounce clock animation
├── inputs.py        Button callback handlers and wiring
└── dog_log.json     Event log (created automatically)
 
```

### Module dependency graph

```
app.py
 ├── hardware    (buttons, device, fonts)
 ├── screens     (UI state, rendering, line builders)
 │    ├── hardware
 │    ├── state
 │    ├── helpers
 │    └── weather
 ├── idle        (animation)
 │    └── hardware
 └── inputs      (button wiring)
      ├── hardware
      └── screens
```

No circular imports. `hardware.py` is the “leaf” — it only depends on external libraries.
