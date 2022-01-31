from requests import Session
from django.conf import settings
from environment.api.auth import refresh_if_expired_and_apply_headers


def api_request(path):
    def send_request(request_creator):
        def wrapper(*args, **kwargs):
            session = Session()
            request = request_creator(*args, **kwargs)
            request.url = f'{settings.RESEARCH_ENVIRONMENT_API_URL}{path}'
            prepped = request.prepare()
            refresh_if_expired_and_apply_headers(prepped)
            return session.send(prepped)
        return wrapper
    return send_request
