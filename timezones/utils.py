from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str
from threading import local
import pytz
from datetime import datetime as dtime


default_tz = pytz.timezone(getattr(settings, "TIME_ZONE", "UTC"))

#Dict to manage thread unique timezone
_timezone = local()


def localtime_for_timezone(value, timezone):
    """
    Given a ``datetime.datetime`` object in UTC and a timezone represented as
    a string, return the localized time for the timezone.
    """
    return adjust_datetime_to_timezone(value, settings.TIME_ZONE, timezone)


def adjust_datetime_to_timezone(value, from_tz, to_tz=None):
    """
    Given a ``datetime`` object adjust it according to the from_tz timezone
    string into the to_tz timezone string.
    """
    if to_tz is None:
        to_tz = settings.TIME_ZONE
    if value.tzinfo is None:
        if not hasattr(from_tz, "localize"):
            from_tz = pytz.timezone(smart_str(from_tz))
        value = from_tz.localize(value)
    return value.astimezone(pytz.timezone(smart_str(to_tz)))


def coerce_timezone_value(value):
    try:
        return pytz.timezone(value)
    except pytz.UnknownTimeZoneError:
        raise ValidationError("Unknown timezone")


def validate_timezone_max_length(max_length, zones):
    def reducer(x, y):
        return x and (len(y) <= max_length)
    if not reduce(reducer, zones, True):
        raise Exception("timezones.fields.TimeZoneField MAX_TIMEZONE_LENGTH is too small")


def activate_timezone(timezone):
    if isinstance(timezone, basestring):
        timezone = smart_str(timezone)
    if timezone in pytz.all_timezones_set:
        timezone = pytz.timezone(timezone)
        
    _timezone.value = timezone

def deactivate_timezone():
    if hasattr(_timezone, 'value'):
        del _timezone.value


def get_timezone():
    timezone = getattr(_timezone, 'value', None)

    if timezone is not None:
        return timezone
    else:
        return default_tz

    from django.conf import settings
    return pytz.timezone(settings.TIME_ZONE)


def set_timezone(dt, tz):
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    if not hasattr(tz, 'localize') and isinstance(tz, str):
        tz = pytz.timezone(tz)

    return tz.localize(dt)


class datetime(dtime):

    @classmethod
    def now(cls, tzinfo=None):
        dt = dtime.now(tzinfo)
        tzone = get_timezone()

        if dt.tzinfo is None:
            dt = default_tz.localize(dt)

        dt = dt.astimezone(tzone)
        return dt




