from django.conf import settings
from django.db import models
from django.utils.encoding import smart_unicode, smart_str
from django.db.models import signals
import pytz, types
from timezones import forms, zones
from timezones.utils import coerce_timezone_value, validate_timezone_max_length



MAX_TIMEZONE_LENGTH = getattr(settings, "MAX_TIMEZONE_LENGTH", 100)
default_tz = pytz.timezone(getattr(settings, "TIME_ZONE", "UTC"))


class TimeZoneField(models.CharField):
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        validate_timezone_max_length(MAX_TIMEZONE_LENGTH, zones.ALL_TIMEZONE_CHOICES)
        defaults = {
            "max_length": MAX_TIMEZONE_LENGTH,
            "default": settings.TIME_ZONE,
            "choices": zones.PRETTY_TIMEZONE_CHOICES
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
    
    def validate(self, value, model_instance):
        # coerce value back to a string to validate correctly
        return super(TimeZoneField, self).validate(smart_str(value), model_instance)
    
    def run_validators(self, value):
        # coerce value back to a string to validate correctly
        return super(TimeZoneField, self).run_validators(smart_str(value))
    
    def to_python(self, value):
        value = super(TimeZoneField, self).to_python(value)
        if value is None:
            return None # null=True
        return coerce_timezone_value(value)
    
    def get_prep_value(self, value):
        if value is not None:
            return smart_unicode(value)
        return value
    
    def get_db_prep_save(self, value, connection=None):
        """
        Prepares the given value for insertion into the database.
        """
        return self.get_prep_value(value)
    
    def flatten_data(self, follow, obj=None):
        value = self._get_val_from_obj(obj)
        if value is None:
            value = ""
        return {self.attname: smart_unicode(value)}


class LocalizedDateTimeField(models.DateTimeField):
    """
    A model field that provides automatic localized timezone support.
    timezone can be a timezone string, a callable (returning a timezone string),
    or a queryset keyword relation for the model, or a pytz.timezone()
    result.
    """
    def __init__(self, verbose_name=None, name=None, timezone=None, **kwargs):
        if isinstance(timezone, basestring):
            timezone = smart_str(timezone)
        if timezone in pytz.all_timezones_set:
            self.timezone = pytz.timezone(timezone)
        else:
            self.timezone = timezone
        super(LocalizedDateTimeField, self).__init__(verbose_name, name, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {"form_class": forms.LocalizedDateTimeField}
        if (not isinstance(self.timezone, basestring) and str(self.timezone) in pytz.all_timezones_set):
            defaults["timezone"] = str(self.timezone)
        defaults.update(kwargs)
        return super(LocalizedDateTimeField, self).formfield(**defaults)
    
    def get_db_prep_save(self, value, connection=None):
        """
        Returns field's value prepared for saving into a database.
        """

        if value is not None:
            if value.tzinfo is not None:
                ## convert to settings.TIME_ZONE
                value = value.astimezone(default_tz)
                
            value = value.replace(tzinfo=None)
        return super(LocalizedDateTimeField, self).get_db_prep_save(value, connection=connection)
    
    @classmethod
    def _add_tz(cls, value):
        if value.tzinfo is not None:
            ## convert to settings.TIME_ZONE
            value = value.astimezone(default_tz)
        value = value.replace(tzinfo=None)
        return value

    def get_db_prep_lookup(self, lookup_type, value, connection=None, prepared=None):
        """
        Returns field's value prepared for database lookup.
        """
        if isinstance(value, types.ListType):
            for i, val in enumerate(value):
                value[i] = self._add_tz(val)
        else:
            value = self._add_tz(value)

        return super(LocalizedDateTimeField, self).get_db_prep_lookup(lookup_type, value, connection=connection, prepared=prepared)

## RED_FLAG: need to add a check at manage.py validation time that
##           time_zone value is a valid query keyword (if it is one)
import signals as tzone_signals

signals.class_prepared.connect(tzone_signals.prep_localized_datetime)
signals.post_init.connect(tzone_signals.init_localized_datetime)

#South migration support
#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^timezones\.fields\.LocalizedDateTimeField"])
