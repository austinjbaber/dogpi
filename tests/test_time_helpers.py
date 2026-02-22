"""Tests for helpers. Run 'python -m pytest' in the terminal."""

from helpers.time_helpers import *
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def morning_afternoon_times():
    return {
        "morning": "2022-02-22T09:00:00",
        "afternoon": "2022-02-22T21:00:00",
    }


@pytest.fixture
def time_deltas():
    """Future 30 mins, past 30 seconds, past 5 minutes, past 1h 5m, past 12h"""
    now = datetime.now()

    return {
        "future_30_mins": (now + timedelta(minutes=30)).isoformat(),
        "past_30_secs": (now - timedelta(seconds=30)).isoformat(),
        "past_5_mins": (now - timedelta(minutes=5)).isoformat(),
        "past_1h_5m": (now - timedelta(hours=1, minutes=5)).isoformat(),
        "past_12h": (now - timedelta(hours=12)).isoformat(),
    }


def test_datetime_to_iso_seconds_pass_None():
    assert datetime_to_iso_seconds(None) == "--"


def test_datetime_to_iso_seconds_pass_invalid():
    assert datetime_to_iso_seconds("test") == "--"


def test_datetime_to_iso_seconds():
    now = datetime.now()
    assert now.isoformat(timespec="seconds") == datetime_to_iso_seconds(now)


def test_get_time_ago_pass_None():
    assert get_time_ago(None) == "never"


def test_get_time_ago_pass_invalid():
    assert get_time_ago("test") == "--"


def test_get_time_ago_future_time(time_deltas):
    assert get_time_ago(time_deltas["future_30_mins"]) == "time is in the future"


def test_get_time_ago_30_secs_ago(time_deltas):
    assert get_time_ago(time_deltas["past_30_secs"]) == "just now"


def test_get_time_ago_5_mins_ago(time_deltas):
    assert get_time_ago(time_deltas["past_5_mins"]) == "5m ago"


def test_get_time_ago_1_hour_5_mins_ago(time_deltas):
    assert get_time_ago(time_deltas["past_1h_5m"]) == "1h 5m ago"


def test_iso_to_compact_time_pass_none():
    assert iso_to_compact_time(None) == "--:--"


def test_iso_to_compact_time_pass_invalid():
    assert iso_to_compact_time("test") == "--"


def test_iso_to_compact_time_pass_morning(morning_afternoon_times):
    assert iso_to_compact_time(morning_afternoon_times["morning"]) == "9:00a"


def test_iso_to_compact_time_pass_afternoon(morning_afternoon_times):
    assert iso_to_compact_time(morning_afternoon_times["afternoon"]) == "9:00p"


def test_iso_to_compact_time_with_time_ago_pass_none():
    assert iso_to_compact_time_with_time_ago(None) == "never"


def test_iso_to_compact_time_with_time_ago_pass_invalid():
    assert iso_to_compact_time_with_time_ago("test") == "-- (--)"


def test_short_time_ago_pass_None():
    assert short_time_ago(None) == "never"


def test_short_time_ago_pass_invalid():
    assert short_time_ago("test") == "--"


def test_short_time_ago_pass_future_30_mins(time_deltas):
    assert short_time_ago(time_deltas["future_30_mins"]) == "time is in the future"


def test_short_time_ago_pass_30_secs_ago(time_deltas):
    assert short_time_ago(time_deltas["past_30_secs"]) == "now"


def test_short_time_ago_pass_5_mins_ago(time_deltas):
    assert short_time_ago(time_deltas["past_5_mins"]) == "5m"


def test_short_time_ago_pass_1h_5m_ago(time_deltas):
    assert short_time_ago(time_deltas["past_1h_5m"]) == "1h5m"


def test_short_time_ago_pass_12h_ago(time_deltas):
    assert short_time_ago(time_deltas["past_12h"]) == ">10h"

def test_get_12_hour_clock_time_pass_None():
    assert get_12_hour_clock_time(None) == "--"

def test_get_12_hour_clock_time_pass_invalid():
    assert get_12_hour_clock_time("test") == "--"

def test_get_12_hour_clock_time_pass_morning(morning_afternoon_times):
    morning_time = datetime.fromisoformat(morning_afternoon_times["morning"]).time()
    assert get_12_hour_clock_time(morning_time) == "9:00 AM"

def test_get_12_hour_clock_time_pass_afternoon(morning_afternoon_times):
    afternoon_time = datetime.fromisoformat(morning_afternoon_times["afternoon"]).time()
    assert get_12_hour_clock_time(afternoon_time) == "9:00 PM"

def test_get_long_date_pass_none():
    assert get_long_date(None) == "--"

def test_get_long_date_pass_invalid():
    assert get_long_date("test") == "--"

def test_get_long_date_pass_date(morning_afternoon_times):
    date = datetime.fromisoformat(morning_afternoon_times["morning"]).date()
    assert get_long_date(date) == "Tue, Feb 22"