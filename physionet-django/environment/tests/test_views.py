from django.test import TestCase


class IdentityProvisioningTestCase(TestCase):
    def test_redirects_to_billing_setup_if_user_has_cloud_identity(self):
        pass


class BillingSetupTestCase(TestCase):
    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        pass

    def test_redirects_to_research_environments_if_user_has_billing_setup(self):
        pass


class ResearchEnvironmentsTestCase(TestCase):
    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        pass

    def test_redirects_to_billing_setup_if_user_has_no_billing_setup(self):
        pass


class CreateResearchEnvironmentTestCase(TestCase):
    def test_redirects_to_identity_provisioning_if_user_has_no_cloud_identity(self):
        pass

    def test_redirects_to_billing_setup_if_user_has_no_billing_setup(self):
        pass
