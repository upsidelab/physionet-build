from unittest import skipIf

from django.test import TestCase
from django.conf import settings

from environment.tests.helpers import (
    create_user_with_cloud_identity,
    create_user_without_cloud_identity,
    create_user_with_billing_setup,
)
from environment.utilities import user_has_cloud_identity, user_has_billing_setup


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class UserHasCloudIdentityTestCase(TestCase):
    def setUp(self):
        self.user_without_cloud_identity = create_user_without_cloud_identity()
        self.user_with_cloud_identity = create_user_with_cloud_identity(
            "laa", "loo", "lee"
        )

    def test_returns_false_for_user_without_cloud_identity(self):
        self.assertFalse(user_has_cloud_identity(self.user_without_cloud_identity))

    def test_returns_true_for_user_with_cloud_identity(self):
        self.assertTrue(user_has_cloud_identity(self.user_with_cloud_identity))


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class UserHasBillingSetupTestCase(TestCase):
    def setUp(self):
        self.user_without_cloud_identity = create_user_without_cloud_identity()
        self.user_with_cloud_identity = create_user_with_cloud_identity(
            "laa", "loo", "lee"
        )
        self.user_with_billing_setup = create_user_with_billing_setup(
            "woo", "waa", "wee"
        )

    def test_returns_false_for_user_without_cloud_identity(self):
        self.assertFalse(user_has_billing_setup(self.user_without_cloud_identity))

    def test_returns_false_for_user_without_billing_setup(self):
        self.assertFalse(user_has_billing_setup(self.user_with_cloud_identity))

    def test_returns_true_for_user_with_billing_setup(self):
        self.assertTrue(user_has_billing_setup(self.user_with_billing_setup))
