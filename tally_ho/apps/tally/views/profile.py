from functools import wraps
from django.conf import settings
from django.contrib.auth import views as auth_views

from django.shortcuts import redirect
from tally_ho.apps.tally.models.user_profile import UserProfile


class PersistSessionVars(object):
    """The logout view, will reset all session state.
    However, we occasionally want to persist some of those session variables,
    for example incase a session expires in the middle of data entry.

    :param object: The list of session variables to be persisted after session
        expiry.
    """

    session_backup = {}

    def __init__(self, session_vars):
        self.session_vars = session_vars

    def __enter__(self):
        for session_var in self.session_vars:
            if self.request.session.get(session_var):
                self.session_backup[session_var] =\
                    self.request.session.get(session_var)

    def __exit__(self, exc_type, exc_value, traceback):
        for session_var in self.session_backup:
            self.request.session[session_var] =\
                self.session_backup.get(session_var)

    def __call__(self, test_func, *args, **kwargs):

        @wraps(test_func)
        def inner(*args, **kwargs):
            if not args:
                raise Exception(
                    str('Must decorate a view, i.e. a function taking request'
                        ' as the first parameter'))
            self.request = args[0]
            with self:
                return test_func(*args, **kwargs)

        return inner


def login(request, *args, **kwargs):
    view = auth_views.LoginView.as_view()
    response = view(request, *args, **kwargs)

    if response.status_code == 302:
        try:
            if request.user.userprofile.reset_password:
                return redirect('password_change')
        except AttributeError:
            pass
        except UserProfile.DoesNotExist:
            profile = UserProfile(user_ptr=request.user)
            profile.save_base(raw=True)

            return redirect('password_change')

    return response


@PersistSessionVars(getattr(settings, "SESSION_VARS"))
def session_expiry_logout_view(request, *args, **kwargs):
    view = auth_views.LogoutView.as_view()
    response = view(request, *args, **kwargs)

    return response
