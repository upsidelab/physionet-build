from unittest import skipIf

from django.test import TestCase
from django.conf import settings

from environment.tests.helpers import (
    create_user_with_cloud_identity,
    create_user_without_cloud_identity,
    create_user_with_billing_setup,
)
from environment.utilities import (
    user_has_cloud_identity,
    user_has_billing_setup,
    left_join_iterators,
    right_join_iterators,
    full_outer_join_iterators,
)


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


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class LeftJoinIteratorsTestCase(TestCase):
    def test_returns_lists_left_joined_on_keys(self):
        list1 = [
            {"id": 1, "data": "anything1"},
            {"id": 2, "data": "anything2"},
            {"id": 3, "data": "anything3"},
            {"id": 4, "data": "anything3"},
        ]
        key_list1 = lambda x: x["id"]
        list2 = [
            {"dataset": 3, "other_data": "anything1"},
            {"dataset": 2, "other_data": "anything2"},
            {"dataset": 1, "other_data": "anything3"},
        ]
        key_list2 = lambda x: x["dataset"]
        left_joined = left_join_iterators(key_list1, list1, key_list2, list2)
        expected_output = [
            (list1[0], list2[2]),
            (list1[1], list2[1]),
            (list1[2], list2[0]),
            (list1[3], None),
        ]
        self.assertEqual(left_joined, expected_output)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class RightJoinIteratorsTestCase(TestCase):
    def test_returns_lists_right_joined_on_keys(self):
        list1 = [
            {"id": 1, "data": "anything1"},
            {"id": 2, "data": "anything2"},
            {"id": 3, "data": "anything3"},
        ]
        key_list1 = lambda x: x["id"]
        list2 = [
            {"dataset": 3, "other_data": "anything1"},
            {"dataset": 2, "other_data": "anything2"},
            {"dataset": 1, "other_data": "anything3"},
            {"dataset": 4, "other_data": "anything3"},
        ]
        key_list2 = lambda x: x["dataset"]
        right_joined = right_join_iterators(key_list1, list1, key_list2, list2)
        expected_output = [
            (list1[2], list2[0]),
            (list1[1], list2[1]),
            (list1[0], list2[2]),
            (None, list2[3]),
        ]
        self.assertEqual(right_joined, expected_output)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class FullOuterJoinIteratorsTestCase(TestCase):
    def test_returns_lists_full_outer_joined_on_keys(self):
        list1 = [
            {"id": 1, "data": "anything1"},
            {"id": 2, "data": "anything2"},
            {"id": 3, "data": "anything3"},
            {"id": 5, "data": "anything3"},
        ]
        key_list1 = lambda x: x["id"]
        list2 = [
            {"dataset": 3, "other_data": "anything1"},
            {"dataset": 2, "other_data": "anything2"},
            {"dataset": 1, "other_data": "anything3"},
            {"dataset": 4, "other_data": "anything3"},
        ]
        key_list2 = lambda x: x["dataset"]
        full_outer_joined = full_outer_join_iterators(
            key_list1, list1, key_list2, list2
        )
        expected_output = [
            (list1[3], None),
            (list1[2], list2[0]),
            (list1[1], list2[1]),
            (list1[0], list2[2]),
            (None, list2[3]),
        ]
        self.assertEqual(full_outer_joined, expected_output)
