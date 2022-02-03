from requests import Request
from django.test import TestCase
from environment.api.auth import apply_api_credentials


class AuthTestCase(TestCase):
    def test_apply_api_credentials_inserting_correct_headers(self):
        request = Request()
        apply_api_credentials(request)

        self.assertIn("authorization", request.headers)
        self.assertRegexpMatches(request.headers["authorization"], r"\ABearer")

    def test_reuses_token_if_not_expired(self):
        request1 = Request()
        apply_api_credentials(request1)
        token1 = request1.headers["authorization"]

        request2 = Request()
        apply_api_credentials(request2)
        token2 = request2.headers["authorization"]

        self.assertEqual(token1, token2)
