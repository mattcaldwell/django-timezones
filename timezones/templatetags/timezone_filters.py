from django.template import defaultfilters
from django.template import Node
from django.template import Library
from utils.models import datetime
from django.utils.translation import ugettext as _

from timezones.utils import localtime_for_timezone

register = Library()

def localtime(value, timezone):
    return localtime_for_timezone(value, timezone)
register.filter("localtime", localtime)

def naturalday(value, arg=None):
    """
        For date values that are tomorrow, today or yesterday compared to
        present day returns representing string. Otherwise, returns a string
        formatted according to settings.DATE_FORMAT.

        Taken from Django and modified to support timezones datetimes.
    """
    try:
        value = datetime(value.year, value.month, value.day).date()
    except AttributeError:
        # Passed value wasn't a date object
        return value
    except ValueError:
        # Date arguments out of range
        return value
    delta = value - datetime.now().date()
    if delta.days == 0:
        return _(u'today')
    elif delta.days == 1:
        return _(u'tomorrow')
    elif delta.days == -1:
        return _(u'yesterday')
    return defaultfilters.date(value, arg)
register.filter(naturalday)

