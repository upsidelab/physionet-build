from functools import wraps
from django.shortcuts import redirect
from environment.utilities import user_has_cloud_identity, user_has_billing_setup


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
    lambda u: not user_has_cloud_identity(u), "identity_provisioning"
)


billing_setup_required = _redirect_view_if_user(
    lambda u: not user_has_billing_setup(u), "billing_setup"
)
