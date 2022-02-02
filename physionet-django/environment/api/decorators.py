from functools import wraps
from requests import Session
from django.conf import settings
from environment.api.auth import apply_api_credentials


def api_request(path):
    def send_request(request_creator_callable):
        @wraps(request_creator_callable)
        def wrapper(*args, **kwargs):
            session = Session()
            request = request_creator_callable(*args, **kwargs)
            request.url = f"{settings.RESEARCH_ENVIRONMENT_API_URL}{path}"
            prepped = request.prepare()
            apply_api_credentials(prepped)
            return session.send(prepped)

        return wrapper

    return send_request
