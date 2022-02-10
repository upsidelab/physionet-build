from typing import Callable

import google.auth.jwt as jwt
from requests import Request
from django.conf import settings


def _generate_credentials() -> jwt.Credentials:
    credentials = jwt.Credentials.from_service_account_file(
        settings.RESEARCH_ENVIRONMENT_API_JWT_SERVICE_ACCOUNT_PATH,
        audience=settings.RESEARCH_ENVIRONMENT_API_JWT_AUDIENCE,
    )
    return credentials


def _credentials_apply_closure() -> Callable[[Request], None]:
    credentials = _generate_credentials()

    def apply_api_credentials(request: Request) -> None:
        credentials.before_request(None, request.method, request.url, request.headers)

    return apply_api_credentials


apply_api_credentials = _credentials_apply_closure()
