"""Stateless time-formatting utilities."""

from datetime import datetime


def iso_from_dt(dt):
    return dt.isoformat(timespec="seconds")


def format_since(iso_ts):
    if not iso_ts:
        return "never"
    t = datetime.fromisoformat(iso_ts)
    delta = datetime.now() - t
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hrs = mins // 60
    mins = mins % 60
    return f"{hrs}h {mins}m ago"


def format_hhmm_ampm(iso_ts):
    if not iso_ts:
        return "--:--"
    t = datetime.fromisoformat(iso_ts)
    return t.strftime("%I:%M %p").lstrip("0")


def format_abs_and_since(iso_ts):
    if not iso_ts:
        return "never"
    return f"{format_hhmm_ampm(iso_ts)} ({format_since(iso_ts)})"
