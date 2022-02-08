from functools import wraps
from typing import Callable

from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from environment.utilities import user_has_cloud_identity, user_has_billing_setup

from user.models import User


def _redirect_view_if_user(predicate: Callable[[User], bool], redirect_url: str):
    def wrapper(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @wraps(view)
        def wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
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
