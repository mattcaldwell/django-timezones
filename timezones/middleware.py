from fields import LocalizedDateTimeField
from utils import activate_timezone

class UserTimezoneMiddleware(object):
    """Set the language as the user language"""

    def process_view(self, request, view_func, view_args, view_kwargs):

        if request.user.is_authenticated():
            profile = request.user.get_profile()

            if profile is not None:
                if hasattr(profile, 'timezone'):
                    activate_timezone(profile.timezone)
                elif hasattr(profile, 'tz'):
                    activate_timezone(profile.tz)

        return
