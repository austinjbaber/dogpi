"""Weather data — Open-Meteo API fetch, caching, and temperature display."""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime

WEATHER_LAT = 32.2226
WEATHER_LON = -110.9747

WEATHER_REFRESH_S = 10 * 60          # fetch at most every 10 minutes
WEATHER_MAX_STALE_S = 2 * 60 * 60    # show cached weather up to 2 hours old

HOURLY_HOURS = 12  # how many hours of forecast to keep

_next_fetch = 0

weather = {
    "fetched_at": 0,
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

# WMO Weather interpretation codes (code -> short description)
_WMO_CODES = {
    0: "Clear",  1: "Mostly Clr", 2: "Partly Cld", 3: "Overcast",
    45: "Fog", 48: "Rime Fog",
    51: "Lt Drzl", 53: "Mod Drzl", 55: "Hvy Drzl",
    56: "Fzg Drzl", 57: "Fzg Drzl",
    61: "Lt Rain", 63: "Mod Rain", 65: "Hvy Rain",
    66: "Fzg Rain", 67: "Fzg Rain",
    71: "Lt Snow", 73: "Mod Snow", 75: "Hvy Snow",
    77: "Grains",
    80: "Lt Shwrs", 81: "Mod Shwrs", 82: "Hvy Shwrs",
    85: "Lt SnShwr", 86: "Hvy SnShwr",
    95: "T-Storm", 96: "T-Strm Hail", 99: "T-Strm Hail",
}

# Compact (<=7‑char) abbreviations suitable for the 128px display
_WMO_ABBR = {
    0: "Clear",  1: "Mostly", 2: "Partly", 3: "Overcst",
    45: "Foggy", 48: "Rimefog",
    51: "Ltdrzl", 53: "Mddrzl", 55: "Hvydrzl",
    56: "Fzgdrzl", 57: "Fzgdrzl",
    61: "Ltrain", 63: "Modrain", 65: "Hvyrain",
    66: "Fzrain", 67: "Fzrain",
    71: "Ltsnow", 73: "Modsnow", 75: "Hvysnow",
    77: "Grains",
    80: "Ltshwr", 81: "Modshwr", 82: "Hvyshwr",
    85: "Ltsnsh", 86: "Hvy snsh",
    95: "Tstorm", 96: "Tshail", 99: "Tshail",
}


def wmo_description(code):
    """Short description for a WMO weather code."""
    try:
        return _WMO_CODES.get(int(code), f"WMO{code}")
    except Exception:
        return "--"


def wmo_abbrev(code):
    """Compact (up to 7‑char) abbreviation for a WMO weather code.

    Returns a mapped abbreviation from _WMO_ABBR when available; otherwise
    derives a short (up to 7‑char) fallback from the full description.
    """
    try:
        i = int(code)
        # explicit compact mapping first
        if i in _WMO_ABBR:
            return _WMO_ABBR[i]
        # fallback: derive from full description (alphanumeric chars)
        desc = _WMO_CODES.get(i)
        if desc:
            token = ''.join(ch for ch in desc if ch.isalnum())[:7]
            return token.capitalize()
        return f"W{i}"
    except Exception:
        return "--"


def _safe_round(x):
    try:
        return int(round(float(x)))
    except Exception:
        return None


def fmt_ampm_from_iso(iso_local):
    """Format an ISO local timestamp as a compact AM/PM string (e.g. '6:30a')."""
    try:
        dt = datetime.fromisoformat(iso_local)
        return dt.strftime("%I:%M%p").lstrip("0").lower().replace("am", "a").replace("pm", "p")
    except Exception:
        return "--"


def deg_to_cardinal(d):
    """Convert degrees to nearest 16-point compass label."""
    try:
        d = float(d)
    except Exception:
        return ""
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    ix = int((d + 11.25) / 22.5) % 16
    return dirs[ix]


def _fetch_openmeteo(lat, lon):
    params = {
        "latitude": f"{lat:.4f}",
        "longitude": f"{lon:.4f}",
        "timezone": "auto",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "forecast_days": "2",
        "current": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "sunrise",
            "sunset",
        ]),
        "hourly": ",".join([
            "temperature_2m",
            "precipitation_probability",
            "weather_code",
        ]),
    }

    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params, safe=",")
    req = urllib.request.Request(url, headers={"User-Agent": "DogPi/1.0"})
    with urllib.request.urlopen(req, timeout=4) as r:
        data = json.loads(r.read().decode("utf-8"))

    cur = data.get("current", {}) or {}
    daily = data.get("daily", {}) or {}

    out = {
        "temp_f": _safe_round(cur.get("temperature_2m")),
        "feels_f": _safe_round(cur.get("apparent_temperature")),
        "rh": _safe_round(cur.get("relative_humidity_2m")),
        "wind_mph": _safe_round(cur.get("wind_speed_10m")),
        "wind_dir": _safe_round(cur.get("wind_direction_10m")),
        "hi_f": None,
        "lo_f": None,
        "pop": None,
        "sunrise": None,
        "sunset": None,
        "hourly": [],
    }

    try:
        out["hi_f"]    = _safe_round(daily.get("temperature_2m_max", [None])[0])
        out["lo_f"]    = _safe_round(daily.get("temperature_2m_min", [None])[0])
        out["pop"]     = _safe_round(daily.get("precipitation_probability_max", [None])[0])
        out["sunrise"] = daily.get("sunrise", [None])[0]
        out["sunset"]  = daily.get("sunset", [None])[0]
    except Exception:
        pass

    # Parse hourly forecast — keep only the next HOURLY_HOURS hours
    hourly_raw = data.get("hourly", {}) or {}
    h_times = hourly_raw.get("time", [])
    h_temps = hourly_raw.get("temperature_2m", [])
    h_pops  = hourly_raw.get("precipitation_probability", [])
    h_codes = hourly_raw.get("weather_code", [])

    now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
    try:
        start_idx = next(i for i, t in enumerate(h_times) if t >= now_str)
    except StopIteration:
        start_idx = len(h_times)

    hourly_out = []
    for i in range(start_idx, min(start_idx + HOURLY_HOURS, len(h_times))):
        try:
            dt = datetime.fromisoformat(h_times[i])
            time_str = dt.strftime("%I%p").lstrip("0").lower()
        except Exception:
            time_str = "?"
        hourly_out.append({
            "time_str": time_str,
            "temp_f": _safe_round(h_temps[i]) if i < len(h_temps) else None,
            "pop": _safe_round(h_pops[i]) if i < len(h_pops) else None,
            "code": h_codes[i] if i < len(h_codes) else None,
            "abbr": wmo_abbrev(h_codes[i]) if i < len(h_codes) else "--",
            "desc": wmo_description(h_codes[i]) if i < len(h_codes) else "--",
        })

    out["hourly"] = hourly_out

    return out


def refresh_if_needed(force=False):
    """Fetch new weather data if the cache has expired (or if *force* is True)."""
    global _next_fetch

    now = time.time()
    if not force and now < _next_fetch:
        return

    _next_fetch = now + WEATHER_REFRESH_S

    try:
        w = _fetch_openmeteo(WEATHER_LAT, WEATHER_LON)
        weather.update(w)
        weather["fetched_at"] = now
        weather["err"] = None
    except Exception as e:
        weather["err"] = str(e)[:60]




def _get_weather_numeric_str(key: str) -> str | None:
    """Generic helper for returning a formatted value from *weather*.

    The caller passes a key such as ``"temp_f"`` or ``"feels_f"`` and this
    function performs the usual staleness check and appends the ``F`` unit.
    ``None`` is returned if the value is missing or too old.
    """
    val = weather.get(key)
    if val is not None:
        age = time.time() - float(weather.get("fetched_at") or 0)
        if age <= WEATHER_MAX_STALE_S:
            return f"{val}F"
    return None


def get_weather_temp_str():
    return _get_weather_numeric_str("temp_f")


def get_weather_feels_str():
    return _get_weather_numeric_str("feels_f")


def get_temp_str():
    """Return a short temperature string for the status screen."""
    refresh_if_needed()

    wx = get_weather_temp_str()
    if wx:
        return wx

    # Fallback: CPU temp (not ambient — placeholder until a sensor is wired)
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            c = float(f.read().strip()) / 1000.0
        f_temp = c * 9.0 / 5.0 + 32.0
        return f"{f_temp:.0f}F"
    except Exception:
        return "--"

