#!/usr/bin/env python3
"""Event list helpers shared by the site build and tests. No network."""
import datetime
from zoneinfo import ZoneInfo

# Event end dates are local calendar dates. Hide once the next day has started
# in that state's time zone. Queensland and the NT do not use daylight saving;
# the IANA zones below handle that through zoneinfo (and Intl in the browser).
EVENT_ZONES = {
    "QLD": "Australia/Brisbane",
    "NSW": "Australia/Sydney",
    "ACT": "Australia/Sydney",
    "VIC": "Australia/Melbourne",
    "SA": "Australia/Adelaide",
    "WA": "Australia/Perth",
    "TAS": "Australia/Hobart",
    "NT": "Australia/Darwin",
}
DEFAULT_ZONE = "Australia/Brisbane"

# Spoken letter names that start with a vowel sound, for initialisms such as AA and NA.
_AN_INITIALS = set("AEFHILMNORSX")


def zone_for(state):
    return EVENT_ZONES.get((state or "").strip().upper(), DEFAULT_ZONE)


def date_in_zone(now, time_zone):
    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.timezone.utc)
    return now.astimezone(ZoneInfo(time_zone)).date().isoformat()


def event_end(event):
    return event.get("end") or event["start"]


def event_is_finished(event, now=None):
    """True once the day after the event's end date has started in its state zone."""
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    end = event_end(event)
    today = date_in_zone(now, zone_for(event.get("state")))
    return today > end


def ev_article(fellowship):
    """'An' before a vowel-sound fellowship name (An AA event, An NA event)."""
    name = (fellowship or "").strip()
    if not name:
        return "A"
    # Short all-caps names (AA, NA, GA, PA) are read as letters; longer names such as SMART are read as a word.
    if name.isalpha() and name.isupper() and len(name) <= 3:
        return "An" if name[0] in _AN_INITIALS else "A"
    return "An" if name[0].upper() in "AEIOU" else "A"
