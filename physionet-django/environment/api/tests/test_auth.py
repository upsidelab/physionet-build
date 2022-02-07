from unittest import skipIf
from unittest.mock import patch, PropertyMock, MagicMock
from requests import Request
from google.auth.credentials import Credentials
from django.test import TestCase
from django.conf import settings
from environment.api.auth import apply_api_credentials


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class AuthTestCase(TestCase):
    def test_apply_api_credentials_inserting_correct_headers(self):
        request = Request()
        apply_api_credentials(request)

        self.assertIn("authorization", request.headers)
        self.assertRegexpMatches(request.headers["authorization"], r"\ABearer")

    @patch.object(Credentials, "refresh", new_callable=MagicMock)
    def test_reuses_token_if_not_expired(self, refresh_mock):
        request1 = Request()
        apply_api_credentials(request1)

        request2 = Request()
        apply_api_credentials(request2)

        refresh_mock.assert_not_called()

    @patch.object(Credentials, "expired", return_value=True, new_callable=PropertyMock)
    @patch.object(Credentials, "refresh", new_callable=MagicMock)
    def test_generates_new_token_if_expired(self, _, refresh_mock):
        request1 = Request()
        apply_api_credentials(request1)

        request2 = Request()
        apply_api_credentials(request2)

        refresh_mock.assert_called()
