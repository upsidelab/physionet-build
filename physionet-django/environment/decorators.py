from functools import wraps
from django.urls import reverse_lazy
from django.shortcuts import redirect


def _user_has_cloud_identity(user):
    return hasattr(user, 'cloud_identity')


def _user_has_billing_setup(user):
    if not _user_has_cloud_identity(user):
        return False
    return hasattr(user.cloud_identity, 'billing_setup')


def _redirect_view_if_user(predicate, redirect_url):
    def wrapper(view):
        @wraps(view)
        def wrapped_view(request, *args, **kwargs):
            if predicate(request.user):
                return redirect(redirect_url)
            return view(request, *args, **kwargs)
        return wrapped_view
    return wrapper


cloud_identity_required = _redirect_view_if_user(
    lambda u: not _user_has_cloud_identity(u),
    'identity_provisioning'
)


skip_if_cloud_identity_exists = _redirect_view_if_user(
    _user_has_cloud_identity,
    'billing_setup'
)


billing_setup_required = _redirect_view_if_user(
    lambda u: not _user_has_billing_setup(u),
    'billing_setup'
)


skip_if_billing_setup_exists = _redirect_view_if_user(
    _user_has_billing_setup,
    'research_environments'
)
