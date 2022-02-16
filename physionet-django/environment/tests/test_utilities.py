from django.test import TestCase


class UserHasCloudIdentityTestCase(TestCase):
    def test_returns_false_for_user_without_cloud_identity(self):
        pass

    def test_returns_true_for_user_with_cloud_identity(self):
        pass


class UserHasBillingSetupTestCase(TestCase):
    def test_returns_false_for_user_without_cloud_identity(self):
        pass

    def test_returns_false_for_user_without_billing_setup(self):
        pass

    def test_returns_true_for_user_with_billing_setup(self):
        pass
