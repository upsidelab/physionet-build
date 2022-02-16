from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase
from django.conf import settings

from environment.services import create_cloud_identity
from environment.exceptions import IdentityProvisioningFailed
from user.models import User


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class CreateCloudIdentityTestCase(TestCase):
    def setUp(self):
        self.some_user = User.objects.first()

    @patch("environment.api.create_cloud_identity")
    def test_raises_if_request_fails(self, mock_create_cloud_identity):
        mock_create_cloud_identity.return_value.ok = False
        self.assertRaises(
            IdentityProvisioningFailed, create_cloud_identity, self.some_user
        )

    @patch("environment.api.create_cloud_identity")
    def test_creates_cloud_identity_if_request_succeeds(
        self, mock_create_cloud_identity
    ):
        mock_otp = "top"
        mock_email = "email"
        mock_create_cloud_identity.return_value.ok = True
        mock_create_cloud_identity.return_value.json.return_value = {
            "one-time-password": mock_otp,
            "email-id": mock_email,
        }

        otp, identity = create_cloud_identity(self.some_user)
        self.assertEqual(otp, mock_otp)
        self.assertEqual(identity.gcp_user_id, self.some_user.username)
        self.assertEqual(identity.email, mock_email)


class VerifyBillingAndCreateWorkspaceTestCase(TestCase):
    def setUp(self):
        self.some_user = User.objects.first()

    @patch("environment.api.create_cloud_identity")
    def test_raises_if_request_fails(self, mock_create_cloud_identity):
        mock_create_cloud_identity.return_value.ok = False
        self.assertRaises(
            IdentityProvisioningFailed, create_cloud_identity, self.some_user
        )
