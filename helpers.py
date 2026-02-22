"""Stateless time-formatting utilities."""

from datetime import datetime


def datetime_to_iso_seconds(dt:datetime):
    return dt.isoformat(timespec="seconds")


def get_time_ago(iso_local):
    if not iso_local:
        return "never"
    local_time = datetime.fromisoformat(iso_local)
    delta = datetime.now() - local_time

    if delta.days < 0:
        return "time is in the future"
    
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hrs = mins // 60
    mins = mins % 60
    return f"{hrs}h {mins}m ago"


def iso_to_compact_time(iso_local:str):
    '''
    Format an ISO local timestamp as a compact AM/PM string (e.g. '6:30a').
    Parameters:
        * iso_local
            * a local ISO 8601 timestamp (without offset) Ex. '2026-02-22T14:37:55'
    '''
    if not iso_local:
        return "--:--"
    
    try:
        dt = datetime.fromisoformat(iso_local)
        return dt.strftime("%I:%M%p").lstrip("0").lower().replace("am", "a").replace("pm", "p")
    except Exception:
        return "--"


def compact_time_with_time_ago(iso_local:str):
    '''
    Returns the compact time with how long ago it was. Ex. '6:30a (5m ago)'
    '''
    if not iso_local:
        return "never"
    return f"{iso_to_compact_time(iso_local)} ({get_time_ago(iso_local)})"


def short_time_ago(iso_local):
    if not iso_local:
        return "never"
    t = datetime.fromisoformat(iso_local)
    mins = int((datetime.now() - t).total_seconds() // 60)
    if mins < 1:
        return "now"
    if mins < 60:
        return f"{mins}m"
    h, m = divmod(mins, 60)
    if h >= 10:
        return ">10h"
    return f"{h}h{m}m"


def deg_to_cardinal(degrees:str):
    """Convert degrees to nearest 16-point compass label."""
    try:
        deg = float(degrees)
        dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
        ix = int((deg + 11.25) / 22.5) % 16
        return dirs[ix]
    except Exception:
        return ""