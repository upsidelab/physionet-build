from django.test import TestCase


class CloudIdentityRequiredTestCase(TestCase):
    def test_redirects_user_without_cloud_identity_to_identity_provisioning(self):
        pass

    def test_does_not_redirect_user_with_cloud_identity(self):
        pass


class BillingSetupRequiredTestCase(TestCase):
    def test_redirects_user_without_billing_account_to_billing_setup(self):
        pass

    def test_does_not_redirect_user_with_billing_account(self):
        pass


class RequirePatchTestCase(TestCase):
    def test_returns_405_for_non_patch_requests(self):
        pass

    def test_succeeds_for_patch_request(self):
        pass


class RequireDeleteTestCase(TestCase):
    def test_returns_405_for_non_delete_requests(self):
        pass

    def test_succeeds_for_delete_request(self):
        pass
