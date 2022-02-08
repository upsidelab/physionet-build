from functools import wraps
from typing import Callable

from requests import Request, Response, Session
from django.conf import settings

from environment.api.auth import apply_api_credentials


def api_request(request_creator_callable: Callable[..., Request]) -> Callable:
    @wraps(request_creator_callable)
    def wrapper(*args, **kwargs) -> Response:
        session = Session()
        request = request_creator_callable(*args, **kwargs)
        request.url = f"{settings.RESEARCH_ENVIRONMENT_API_URL}{request.url}"
        prepped = request.prepare()
        apply_api_credentials(prepped)
        return session.send(prepped)

    return wrapper
