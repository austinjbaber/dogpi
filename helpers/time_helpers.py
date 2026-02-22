"""Stateless utilities for time formatting"""

from datetime import datetime, time, date


def datetime_to_iso_seconds(dt:datetime):
    if not dt:
        return "--"
    
    try:
        return dt.isoformat(timespec="seconds")
    except Exception:
        return "--"


def get_time_ago(iso_local):
    if not iso_local:
        return "never"
    
    try:
        local_time = datetime.fromisoformat(iso_local)
        delta = datetime.now() - local_time
    except Exception:
        return "--"

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


def iso_to_compact_time_with_time_ago(iso_local:str):
    '''
    Returns the compact time with how long ago it was. Ex. '6:30a (5m ago)'
    '''
    if not iso_local:
        return "never"
    

    return f"{iso_to_compact_time(iso_local)} ({get_time_ago(iso_local)})"


def short_time_ago(iso_local):
    if not iso_local:
        return "never"
    try:
        current_time = datetime.fromisoformat(iso_local)
        mins = (datetime.now() - current_time).total_seconds() / 60
    except Exception:
        return "--"
    
    if mins < 0 :
        return "time is in the future"

    if mins < 1 and mins > 0:
        return "now"
    
    mins = int(mins)
    
    if mins < 60:
        return f"{mins}m"
    h, m = divmod(mins, 60)
    if h >= 10:
        return ">10h"
    return f"{h}h{m}m"

    
def get_12_hour_clock_time(time:time):
    '''Returns the 12 hour clock format, without leading zeros. Eg. 6:30 AM'''
    try:
        if not time:
            return "--"
        
        return time.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return "--"
    

def get_long_date(date:date):
    '''Returns the date formated as 'weekday name, month name day of month' without the year.'''
    try:
        if not date:
            return "--"
        
        return date.strftime("%a, %b %d")
    except Exception:
        return "--"