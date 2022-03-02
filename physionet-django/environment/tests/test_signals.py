from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class UserSignalsTestCase(TestCase):
    def memoizes_original_credentialing_on_init(self):
        new_user = User()
        self.assertEqual(new_user._original_is_credentialed, new_user.is_credentialed())

    @patch("environment.tasks.stop_environments_with_expired_access")
    def schedules_task_on_save_if_credentialing_was_revoked(
        self, stop_environments_with_expired_access_mock
    ):
        new_user = User()
        new_user.is_credentialed = True
        new_user.save()
        stop_environments_with_expired_access_mock.assert_called()


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class UserSignalsTestCase(TestCase):
    def memoizes_original_credentialing_on_init(self):
        new_user = User()
        self.assertEqual(new_user._original_is_credentialed, new_user.is_credentialed())

    @patch("environment.tasks.stop_environments_with_expired_access")
    def schedules_task_on_save_if_credentialing_was_revoked(
        self, stop_environments_with_expired_access_mock
    ):
        new_user = User()
        new_user.is_credentialed = True
        new_user.save()
        stop_environments_with_expired_access_mock.assert_called()
