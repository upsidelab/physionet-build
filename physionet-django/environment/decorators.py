from functools import wraps
from django.urls import reverse_lazy
from django.shortcuts import redirect


def _user_has_cloud_identity(user):
    return hasattr(user, 'cloud_identity')


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
    reverse_lazy('identity_provisioning')
)


skip_if_cloud_identity_exists = _redirect_view_if_user(
    _user_has_cloud_identity,
    reverse_lazy('research_environments')
)


# billing_setup_required = _redirect_view_if(
#     lambda u: not _user_has_billing_setup(u),
#     reverse_lazy('research_environments')
# )
