from requests import Request, Session
from unittest import skipIf
from unittest.mock import patch, Mock
from django.test import TestCase
from django.conf import settings
from environment.api.decorators import api_request


SAMPLE_ENDPOINT = "/some_path"


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class DecoratorsTestCase(TestCase):
    def setUp(self):
        session_send_patcher = patch.object(Session, "send")
        self.session_send_mock = session_send_patcher.start()
        self.session_send_mock.return_value = Mock()

        self.addCleanup(session_send_patcher.stop)

    def test_sends_the_prepared_request(self):
        self._decorate_and_call()

        self.session_send_mock.assert_called_once()

    def test_sets_the_request_url(self):
        self._decorate_and_call()
        sent_request = self.session_send_mock.call_args[0][0]

        self.assertEqual(
            sent_request.url,
            f"{settings.RESEARCH_ENVIRONMENT_API_URL}{SAMPLE_ENDPOINT}",
        )

    def test_applies_authorization(self):
        self._decorate_and_call()
        sent_request = self.session_send_mock.call_args[0][0]

        self.assertIn("authorization", sent_request.headers)

    def _decorate_and_call(self):
        request_fun = lambda: Request()
        decorated_fun = api_request(SAMPLE_ENDPOINT)(request_fun)
        decorated_fun()
