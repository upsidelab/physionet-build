from typing import Callable
from functools import wraps

from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Model

from environment.utilities import (
    user_has_cloud_identity,
    user_has_billing_setup,
    user_workspace_setup_done,
)


View = Callable[[HttpRequest], HttpResponse]

User = Model


def _redirect_view_if_user(predicate: Callable[[User], bool], redirect_url: str):
    def wrapper(view: View) -> View:
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

workspace_setup_required = _redirect_view_if_user(
    lambda u: not user_workspace_setup_done(u), "workspace_setup"
)


require_PATCH = require_http_methods(["PATCH"])


require_DELETE = require_http_methods(["DELETE"])
