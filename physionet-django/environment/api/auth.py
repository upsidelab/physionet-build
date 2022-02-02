import google.auth.jwt as jwt
from django.conf import settings


def _generate_credentials():
    credentials = jwt.Credentials.from_service_account_file(
        settings.RESEARCH_ENVIRONMENT_API_JWT_SERVICE_ACCOUNT_PATH,
        audience=settings.RESEARCH_ENVIRONMENT_API_JWT_AUDIENCE,
    )
    credentials.refresh(None)
    return credentials


def _credentials_apply_closure():
    credentials = _generate_credentials()

    def apply_api_credentials(request):
        credentials.before_request(None, request.method, request.url, request.headers)

    return apply_api_credentials


apply_api_credentials = _credentials_apply_closure()
