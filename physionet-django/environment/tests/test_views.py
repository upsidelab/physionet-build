from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from environment.tests.helpers import (
    create_user_without_cloud_identity,
    create_user_with_cloud_identity,
    create_user_with_billing_setup,
)
from environment.exceptions import BillingVerificationFailed


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class IdentityProvisioningTestCase(TestCase):
    url = reverse("identity_provisioning")

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?next={self.url}"
        self.assertRedirects(response, redirect_url)

    def test_redirects_to_billing_setup_if_user_has_cloud_identity(self):
        user = create_user_with_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("billing_setup"))

    @patch("environment.services.create_cloud_identity")
    def test_redirects_to_billing_setup_after_creating_identity(
        self, mock_create_cloud_identity
    ):
        mock_create_cloud_identity.return_value = ("otp", "identity_object")
        user = create_user_without_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.post(self.url)
        mock_create_cloud_identity.assert_called()
        self.assertRedirects(
            response, reverse("billing_setup"), fetch_redirect_response=False
        )

    @patch("environment.services.create_cloud_identity")
    def test_saves_one_time_password_in_session(self, mock_create_cloud_identity):
        otp = "otp"
        mock_create_cloud_identity.return_value = (otp, "identity object")
        user = create_user_without_cloud_identity()
        self.client.force_login(user=user)

        self.client.post(self.url)
        self.assertEqual(self.client.session["cloud_identity_otp"], otp)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class BillingSetupTestCase(TestCase):
    url = reverse("billing_setup")

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?next={self.url}"
        self.assertRedirects(response, redirect_url)

    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        user = create_user_without_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("identity_provisioning"))

    def test_redirects_to_research_environments_if_user_has_billing_setup(self):
        user = create_user_with_billing_setup()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse("research_environments"), fetch_redirect_response=False
        )

    @patch("environment.services.create_billing_setup")
    def test_does_not_create_billing_setup_when_supplied_with_invalid_data(
        self, mock_create_billing_setup
    ):
        user = create_user_with_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.post(
            self.url, {"billing_account_id": "some invalid data"}
        )
        mock_create_billing_setup.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch("environment.services.verify_billing_and_create_workspace")
    @patch("environment.services.create_billing_setup")
    def test_does_not_create_billing_setup_when_billing_verification_fails(
        self, mock_create_billing_setup, mock_verify_billing_and_create_workspace
    ):
        mock_verify_billing_and_create_workspace.side_effect = (
            BillingVerificationFailed()
        )
        user = create_user_with_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.post(
            self.url, {"billing_account_id": "some invalid data"}
        )
        mock_create_billing_setup.assert_not_called()
        self.assertEqual(response.status_code, 200)

    @patch("environment.services.verify_billing_and_create_workspace")
    @patch("environment.services.create_billing_setup")
    def test_creates_billing_setup_and_redirects_to_environments(
        self, mock_create_billing_setup, mock_verify_billing_and_create_workspace
    ):
        user = create_user_with_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.post(
            self.url, {"billing_account_id": "XXXXXX-XXXXXX-XXXXXX"}
        )
        mock_create_billing_setup.assert_called()
        mock_verify_billing_and_create_workspace.assert_called()
        self.assertRedirects(
            response, reverse("research_environments"), fetch_redirect_response=False
        )


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class ResearchEnvironmentsTestCase(TestCase):
    url = reverse("research_environments")

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?next={self.url}"
        self.assertRedirects(response, redirect_url)

    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        user = create_user_without_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("identity_provisioning"))

    def test_redirects_to_billing_setup_if_user_has_no_billing_setup(self):
        user = create_user_with_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("billing_setup"))

    @patch("environment.services.get_available_projects_with_environments")
    @patch("environment.services.get_environments_with_projects")
    def test_fetches_and_matches_available_environments_and_projects(
        self,
        mock_get_available_projects_with_environments,
        mock_get_environments_with_projects,
    ):
        user = create_user_with_billing_setup()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        mock_get_environments_with_projects.assert_called()
        mock_get_available_projects_with_environments.assert_called()
        self.assertEqual(response.status_code, 200)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class CreateResearchEnvironmentTestCase(TestCase):
    url = reverse(
        "create_research_environment",
        kwargs={"project_slug": "some_slug", "project_version": "some_version"},
    )

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?next={self.url}"
        self.assertRedirects(response, redirect_url)

    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        user = create_user_without_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("identity_provisioning"))

    def test_redirects_to_billing_setup_if_user_has_no_billing_setup(self):
        user = create_user_with_cloud_identity()
        self.client.force_login(user=user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("billing_setup"))
