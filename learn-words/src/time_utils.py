"""A module for time-related utility functions."""

from datetime import datetime, timedelta, time


def parse_utc_offset(tz_str: str) -> int:
    """Parse a UTC offset string (e.g., 'UTC+3') and return the offset in hours."""
    if not tz_str or not tz_str.startswith("UTC"):
        return 0
    try:
        return int(tz_str[3:])
    except (ValueError, IndexError):
        return 0


def convert_utc_to_local_time(utc_time_str: str, tz_str: str) -> str:
    """Convert a UTC time string to a local time string."""
    offset = parse_utc_offset(tz_str)
    utc_time = datetime.strptime(utc_time_str, "%H:%M").time()

    # Create a datetime object to perform the conversion
    dt = datetime.combine(datetime.utcnow().date(), utc_time)
    local_dt = dt + timedelta(hours=offset)

    return local_dt.strftime("%H:%M")


def convert_local_to_utc_time(local_time_str: str, tz_str: str) -> str:
    """Convert a local time string to a UTC time string."""
    offset = parse_utc_offset(tz_str)
    local_time = datetime.strptime(local_time_str, "%H:%M").time()

    # Create a datetime object to perform the conversion
    dt = datetime.combine(datetime.utcnow().date(), local_time)
    utc_dt = dt - timedelta(hours=offset)

    return utc_dt.strftime("%H:%M")
