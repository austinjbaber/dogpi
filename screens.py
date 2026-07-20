"""Screen content builders, shared UI state, rendering, and toast."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import time

from hardware import device, SCREEN_FONT, WHEN_FONT
from state import log_event, last_dog_where, undo_last_dog_event
from helpers import *
from services import IWeatherService
from services.weather.models import HourForecast

# ----------------------------
# Mode constants
# ----------------------------
MODE_IDLE    = "idle"
MODE_STATUS  = "status"
MODE_MENU    = "menu"
MODE_WHEN    = "when"
MODE_WEATHER = "weather"
MODE_FORECAST = "forecast"

IDLE_TIMEOUT_S = 25  # seconds of inactivity before returning to idle

# ----------------------------
# Shared mutable UI state
# ----------------------------
@dataclass
class UIState:
    mode: str = MODE_IDLE
    menu_idx: int = 0
    weather_scroll: int = 0
    forecast_scroll: int = 0
    when_hours: int = 0
    when_min_idx: int = 0
    when_field: str = "hours"
    pending_log_value: object = None
    sel_was_held: bool = False
    toast_lines: object = None
    toast_until: float = 0.0
    last_input_t: float = 0.0


@dataclass
class HourlyWeatherView:
    time_str: str = "?"
    temp_f: int | None = None
    pop: int | None = None
    code: int | None = None
    abbr: str | None = None
    desc: str | None = None


@dataclass
class WeatherViewState:
    fetched_at: str | None = None
    fetched_ts: float = 0.0
    temp_f: int | None = None
    feels_f: int | None = None
    rh: int | None = None
    wind_mph: int | None = None
    wind_dir: int | None = None
    pop: int | None = None
    hi_f: int | None = None
    lo_f: int | None = None
    sunrise: str | None = None
    sunset: str | None = None
    hourly: list[HourlyWeatherView] = field(default_factory=list)
    err: str | None = None
    is_stale: bool = False


ui = UIState(last_input_t=time.monotonic())
weather = WeatherViewState()

_weather_service: IWeatherService | None = None


def configure_weather_service(service: IWeatherService) -> None:
    """Set the weather service used by screen content builders."""
    global _weather_service
    _weather_service = service

# ----------------------------
# Menu definition
# ----------------------------
MINUTES_OPTIONS = [0, 15, 30, 45]
MAX_WHEN_HOURS  = 9

menu = [
    ("Log pee",  {"type": "dog", "value": "pee"}),
    ("Log poop", {"type": "dog", "value": "poop"}),
    ("Log both", {"type": "dog", "value": "both"}),
    ("Undo",      {"type": "undo"}),
    ("Weather",  {"type": "weather"}),
    ("Forecast", {"type": "forecast"}),
]

# ----------------------------
# Rendering
# ----------------------------
def render_lines(lines, font=SCREEN_FONT):
    img = Image.new("1", device.size, 0)
    draw = ImageDraw.Draw(img)

    bbox = font.getbbox("Ag")
    font_h = bbox[3] - bbox[1]
    line_h = font_h + 1
    max_lines = device.height // line_h

    width = device.size[0]

    y = 0
    for line in lines[:max_lines]:
        # Support a few line formats:
        #  - string -> left-aligned
        #  - (text, align) where align in ('left','center','right') -> single text with given alignment
        #  - (left_text, right_text) -> draw left_text at left and right_text right-aligned on same line
        if isinstance(line, tuple):
            if len(line) == 2 and isinstance(line[1], str) and line[1] in ("left", "center", "right"):
                text, align = line
                bbox = font.getbbox(text)
                text_w = bbox[2] - bbox[0]
                if align == "left":
                    x = 0
                elif align == "center":
                    x = max(0, (width - text_w) // 2)
                else:  # right
                    x = max(0, width - text_w)
                draw.text((x, y), text, font=font, fill=255)
            else:
                # assume two textual parts: left and right
                left_text = str(line[0])
                right_text = str(line[1])
                draw.text((0, y), left_text, font=font, fill=255)
                rbbox = font.getbbox(right_text)
                rw = rbbox[2] - rbbox[0]
                rx = max(0, width - rw)
                draw.text((rx, y), right_text, font=font, fill=255)
        else:
            draw.text((0, y), str(line), font=font, fill=255)

        y += line_h

    device.display(img)

# ----------------------------
# Toast
# ----------------------------
def show_toast(lines, seconds=2.0):
    ui.toast_lines = lines if isinstance(lines, list) else [str(lines)]
    ui.toast_until = time.time() + seconds

# ----------------------------
# Menu actions
# ----------------------------
def do_menu_action(action):
    if action["type"] == "dog":
        ui.pending_log_value = action["value"]
        ui.when_hours = 0
        ui.when_min_idx = 0
        ui.when_field = "hours"
        ui.mode = MODE_WHEN
        return

    if action["type"] == "weather":
        ui.weather_scroll = 0
        ui.mode = MODE_WEATHER
        return

    if action["type"] == "forecast":
        ui.forecast_scroll = 0
        ui.mode = MODE_FORECAST
        return

    if action["type"] == "undo":
        removed = undo_last_dog_event()
        if removed:
            show_toast(f"Undid: {removed.get('value')} at {iso_to_compact_time(removed.get('ts'))}")
        else:
            show_toast("Nothing to undo")
        ui.mode = MODE_STATUS
        return

    if action["type"] == "back":
        ui.mode = MODE_STATUS
        return


def commit_pending_log():
    mins = MINUTES_OPTIONS[ui.when_min_idx]
    seconds_ago = ui.when_hours * 3600 + mins * 60

    dt = datetime_to_iso_seconds(datetime.now() - timedelta(seconds=seconds_ago))
    log_event({"type": "dog", "value": ui.pending_log_value, "ts": dt})

    if seconds_ago == 0:
        show_toast(f"Logged: {ui.pending_log_value}")
    else:
        label = iso_to_compact_time_with_time_ago(dt)
        show_toast([f"Logged: {ui.pending_log_value}", f"{label}"])

    ui.pending_log_value = None
    ui.mode = MODE_STATUS

# ----------------------------
# Line builders
# ----------------------------
def status_lines():
    weather_refresh()
    now = datetime.now()
    temp = weather.temp_f
    feels = weather.feels_f

    if temp and feels:
        right = f"{temp} / {feels}F"
    elif temp:
        right = f"{temp}F"
    else:
        right = "Temp: --"

    last_pee  = last_dog_where(lambda e: e.get("value") in ("pee", "both"))
    last_poop = last_dog_where(lambda e: e.get("value") in ("poop", "both"))

    time_str = get_12_hour_clock_time(now.time())
    date_str = get_long_date(now.date())
    lines = [(time_str, right), (date_str, "center"), ""]

    if last_pee and last_poop and last_pee.get("ts") == last_poop.get("ts"):
        ts = last_pee["ts"]
        lines.append(f"Both: {iso_to_compact_time(ts)} ({short_time_ago(ts)})")
    else:
        if last_pee:
            ts = last_pee["ts"]
            lines.append(f"Pee: {iso_to_compact_time(ts)} ({short_time_ago(ts)})")
        else:
            lines.append("Pee: --:--  never")

        if last_poop:
            ts = last_poop["ts"]
            lines.append(f"Poo: {iso_to_compact_time(ts)} ({short_time_ago(ts)})")
        else:
            lines.append("Both: --:--  never")

    return lines


def menu_lines():
    start = max(0, min(ui.menu_idx - 1, len(menu) - 4))
    view = menu[start:start + 4]
    lines = ["Menu:"]
    for i, (label, _) in enumerate(view, start=start):
        prefix = ">" if i == ui.menu_idx else " "
        lines.append(f"{prefix} {label}")
    lines.append("UP/DN move")
    lines.append("SEL choose")
    return lines


def when_lines():
    title = ui.pending_log_value or "?"
    hrs = ui.when_hours
    mins = MINUTES_OPTIONS[ui.when_min_idx]
    # compute the actual clock time that corresponds to the "how long ago" selection
    seconds_ago = hrs * 3600 + mins * 60
    dt = datetime.now() - timedelta(seconds=seconds_ago)

    time_str = get_12_hour_clock_time(dt.time())
    
    # The [] tell the user where they are inputting values
    if ui.when_field == "hours":
        when_str = f"[{hrs}h] {mins}m ago"
    else:
        when_str = f"{hrs}h [{mins}m] ago"

    return [
        f"Log: {title}",
        "",
        when_str,
        f"At: {time_str}",
    ]

def _safe_display(val, suffix=""):
    """Format a value with a fallback of '--'."""
    return f"{val}{suffix}" if val is not None else f"--{suffix}"


def weather_lines():
    weather_refresh()

    t = weather.temp_f
    f = weather.feels_f
    rh = weather.rh
    wind = weather.wind_mph
    wind_dir = weather.wind_dir
    pop = weather.pop
    hi = weather.hi_f
    lo = weather.lo_f
    sr = iso_to_compact_time(weather.sunrise)
    ss = iso_to_compact_time(weather.sunset)

    wd_card = deg_to_cardinal(wind_dir) if wind_dir is not None else ""
    wind_str = f"{_safe_display(wind, 'mph')} {wd_card}".strip()

    fetched_ts = weather.fetched_ts
    age_m = int(max(0, (time.time() - float(fetched_ts)) // 60)) if fetched_ts else 0
    stale = "" if age_m < 60 else f" ({age_m // 60}h)"

    fetched_at = weather.fetched_at
    if fetched_at:
        fetched_str = iso_to_compact_time(fetched_at)
    else:
        fetched_str = "--:--"
    fetched_age = f"{age_m}m ago{stale}" if fetched_ts else "never"

    C = "center"  # shorthand
    lines = [
        (f"Now: {_safe_display(t, 'F')}", C),
        (f"Feels: {_safe_display(f, 'F')}", C),
        (f"Rain: {_safe_display(pop, '%')}", C),
        (f"Wind: {wind_str}", C),
        (f"Humidity: {_safe_display(rh, '%')}", C),
        (f"Hi: {_safe_display(hi, 'F')}  Lo: {_safe_display(lo, 'F')}", C),
        (f"Sunrise: {sr}", C),
        (f"Sunset: {ss}", C),
        (f"{fetched_str}  {fetched_age}", C),
    ]

    err = weather.err
    if err:
        lines.append((f"Err: {err}", C))

    return lines


def forecast_lines():
    """Build scrollable hourly forecast lines."""
    weather_refresh()

    hourly = weather.hourly
    if not hourly:
        return [("No forecast data", "center")]

    L = "left"
    lines = [("-- Hourly Forecast --","center")]

    for h in hourly:
        time_str = h.time_str
        temp = _safe_display(h.temp_f, "F")
        pop = _safe_display(h.pop, "%")
        abbr = h.abbr or ""
        lines.append((f"{time_str}  {temp}  {pop}  {abbr}", L))

    return lines

def process_hourly_forecast(forecast: list[HourForecast]) -> list[HourlyWeatherView]:
    hourly: list[HourlyWeatherView] = []
    for hour in forecast:
        if hour.time:
            time_str = hour.time.strftime("%I%p").lstrip("0").lower()
        else:
            time_str = "?"
        hourly.append(
            HourlyWeatherView(
                time_str=time_str,
                temp_f=hour.temperature.fahrenheit if hour.temperature else None,
                pop=hour.precipitation_probability,
                code=hour.weather_code,
                abbr=hour.wmo_abbr,
                desc=hour.wmo_desc,
            )
        )
    return hourly

def weather_refresh():
    global weather
    try:
        if _weather_service is None:
            weather.err = "Weather service unavailable"
            return

        weather_result = _weather_service.get_weather_data()
        weather_data = weather_result.data
        if not weather_data:
            weather.err = weather_result.error or "Weather unavailable"
            weather.is_stale = weather_result.is_stale
            return

        weather = WeatherViewState(
            fetched_at=datetime_to_iso_seconds(weather_data.observed_at),
            fetched_ts=weather_data.observed_at.timestamp() if weather_data.observed_at else 0.0,
            temp_f=weather_data.current.temperature.fahrenheit,
            feels_f=weather_data.current.apparent_temperature.fahrenheit,
            rh=weather_data.current.relative_humidity,
            wind_mph=weather_data.current.wind.speed_mph,
            wind_dir=weather_data.current.wind.direction,
            pop=weather_data.daily.precipitation_probability,
            hi_f=weather_data.daily.high.fahrenheit,
            lo_f=weather_data.daily.low.fahrenheit,
            sunrise=datetime_to_iso_seconds(weather_data.daily.sunrise),
            sunset=datetime_to_iso_seconds(weather_data.daily.sunset),
            hourly=process_hourly_forecast(weather_data.hourly),
            err=weather_result.error,
            is_stale=weather_result.is_stale,
        )
    except Exception as exc:
        weather.err = str(exc)[:60]
