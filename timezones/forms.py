from django import forms
from django.conf import settings
from django.utils.encoding import smart_str

import pytz

from timezones import zones
from timezones.utils import adjust_datetime_to_timezone, coerce_timezone_value, get_timezone

default_tz = pytz.timezone(getattr(settings, "TIME_ZONE", "UTC"))



class TimeZoneField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        if not "choices" in kwargs:
            kwargs["choices"] = zones.PRETTY_TIMEZONE_CHOICES
        kwargs["coerce"] = coerce_timezone_value
        super(TimeZoneField, self).__init__(*args, **kwargs)


class LocalizedDateTimeField(forms.DateTimeField):
    """
    Converts the datetime from the user timezone to settings.TIME_ZONE.
    """
    def __init__(self, timezone=None, *args, **kwargs):
        super(LocalizedDateTimeField, self).__init__(*args, **kwargs)
        self.timezone = timezone or get_timezone()

    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        if value is None: # field was likely not required
            return None
        if not hasattr(self.timezone, 'localize'):
            self.timezone = pytz.timezone(smart_str(get_timezone()))
        value = self.timezone.localize(value)
        return value
