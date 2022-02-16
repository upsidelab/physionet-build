from django.test import TestCase
from django.urls import reverse

from environment.tests.helpers import create_user_without_cloud_identity, create_user_with_cloud_identity, create_user_with_billing_setup


class IdentityProvisioningTestCase(TestCase):
    url = reverse("identity_provisioning")

    def test_redirects_to_billing_setup_if_user_has_cloud_identity(self):
        user = create_user_with_cloud_identity()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class BillingSetupTestCase(TestCase):
    url = reverse("billing_setup")

    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        user = create_user_without_cloud_identity()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_research_environments_if_user_has_billing_setup(self):
        user = create_user_with_billing_setup()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class ResearchEnvironmentsTestCase(TestCase):
    url = reverse("research_environments")

    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        user = create_user_without_cloud_identity()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_billing_setup_if_user_has_no_billing_setup(self):
        user = create_user_with_cloud_identity()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class CreateResearchEnvironmentTestCase(TestCase):
    url = reverse("create_research_environment")

    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        user = create_user_without_cloud_identity()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_billing_setup_if_user_has_no_billing_setup(self):
        user = create_user_with_cloud_identity()
        self.client.login(username=user.username, password="password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
