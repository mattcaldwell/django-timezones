from django.utils.encoding import smart_str
import pytz
from fields import LocalizedDateTimeField
from utils import get_timezone
from django.conf import settings


default_tz = pytz.timezone(getattr(settings, "TIME_ZONE", "UTC"))


def prep_localized_datetime(sender, **kwargs):
    for field in sender._meta.fields:
        if not isinstance(field, LocalizedDateTimeField) or field.timezone is None:
            continue
        dt_field_name = "_datetimezone_%s" % field.attname
        def get_dtz_field(instance):
            return getattr(instance, dt_field_name)
        def set_dtz_field(instance, dt):
            if dt.tzinfo is None:
                dt = default_tz.localize(dt)
            time_zone = field.timezone
            if isinstance(field.timezone, basestring):
                tz_name = instance._default_manager.filter(
                    pk=instance._get_pk_val()
                ).values_list(field.timezone)[0][0]
                try:
                    time_zone = pytz.timezone(tz_name)
                except:
                    time_zone = default_tz
                if time_zone is None:
                    # lookup failed
                    time_zone = default_tz
                    #raise pytz.UnknownTimeZoneError(
                    #    "Time zone %r from relation %r was not found"
                    #    % (tz_name, field.timezone)
                    #)
            elif callable(time_zone):
                tz_name = time_zone()
                if isinstance(tz_name, basestring):
                    try:
                        time_zone = pytz.timezone(tz_name)
                    except:
                        time_zone = default_tz
                else:
                    time_zone = tz_name
                if time_zone is None:
                    # lookup failed
                    time_zone = default_tz
                    #raise pytz.UnknownTimeZoneError(
                    #    "Time zone %r from callable %r was not found"
                    #    % (tz_name, field.timezone)
                    #)
            setattr(instance, dt_field_name, dt.astimezone(time_zone))
        setattr(sender, field.attname, property(get_dtz_field, set_dtz_field))

def init_localized_datetime(instance, **kwargs):
    for field in instance.__class__._meta.fields:
        if not isinstance(field, LocalizedDateTimeField):
            continue

        attname = field.attname
        dt = getattr(instance, attname, None)
        if dt is not None:
            tzone = get_timezone()
            if isinstance(tzone, basestring):
                tzone = smart_str(tzone)
                if tzone in pytz.all_timezones_set:
                    tzone = pytz.timezone(tzone)                

            if dt.tzinfo is None:
                dt = default_tz.localize(dt)

            dt = dt.astimezone(tzone)
            setattr(instance, attname, dt)

