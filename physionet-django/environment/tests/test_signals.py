from datetime import timedelta
from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from environment.signals import User, DataAccessRequest, Training


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class UserSignalsTestCase(TestCase):
    def test_memoizes_original_credentialing_on_init(self):
        new_user = User()
        self.assertEqual(new_user._original_is_credentialed, new_user.is_credentialed)

    @patch("environment.signals.stop_environments_with_expired_access")
    def test_does_not_schedule_task_on_save_if_user_has_no_billing_setup(
        self, mock_stop_environments_with_expired_access
    ):
        new_user = User(is_credentialed=True)
        new_user.is_credentialed = False
        new_user.save()
        mock_stop_environments_with_expired_access.assert_not_called()

    @patch("environment.signals.stop_environments_with_expired_access")
    @patch("environment.signals.user_has_billing_setup")
    def test_schedules_task_on_save_if_credentialing_was_revoked(
        self, mock_user_has_billing_setup, mock_stop_environments_with_expired_access
    ):
        mock_user_has_billing_setup.return_value = True
        new_user = User(is_credentialed=True)
        new_user.is_credentialed = False
        new_user.save()
        mock_stop_environments_with_expired_access.assert_called()


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class TrainingSignalsTestCase(TestCase):
    def test_memoizes_original_validity_on_init(self):
        new_user = User()
        new_user.save()
        new_training = Training(user=new_user, training_type_id=1)
        self.assertEqual(new_training._original_is_valid, new_training.is_valid())

    @patch("environment.signals.stop_environments_with_expired_access")
    def test_does_not_schedule_task_on_save_if_user_has_no_billing_setup(
        self, mock_stop_environments_with_expired_access
    ):
        new_user = User()
        new_user.save()
        new_training = Training(user=new_user, training_type_id=1)
        new_training.save()
        mock_stop_environments_with_expired_access.assert_not_called()

    @patch("environment.signals.stop_environments_with_expired_access")
    @patch("environment.signals.user_has_billing_setup")
    def test_schedules_task_on_save_if_training_was_accepted(
        self, mock_user_has_billing_setup, mock_stop_environments_with_expired_access
    ):
        mock_user_has_billing_setup.return_value = True
        new_user = User()
        new_user.save()
        new_training = Training(
            user=new_user, process_datetime=timezone.now(), training_type_id=1
        )
        new_training._original_is_valid = False
        new_training.is_valid = lambda: True
        new_training.save()
        mock_stop_environments_with_expired_access.assert_called()


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class DataAccessRequestSignalsTestCase(TestCase):
    def test_memoizes_original_is_accepted_on_init(self):
        new_access_request = DataAccessRequest()
        self.assertEqual(
            new_access_request._original_is_accepted, new_access_request.is_accepted()
        )

    def test_memoizes_original_is_revoked_on_init(self):
        new_access_request = DataAccessRequest()
        self.assertEqual(
            new_access_request._original_is_revoked, new_access_request.is_revoked()
        )

    @patch("environment.signals.stop_environments_with_expired_access")
    def test_does_not_schedule_task_on_save_if_user_has_no_billing_setup(
        self, mock_stop_environments_with_expired_access
    ):
        requester = User()
        requester.save()
        new_data_access_request = DataAccessRequest(
            requester=requester, project_id=1, duration=timedelta(days=10)
        )
        new_data_access_request._original_is_accepted = False
        new_data_access_request.is_accepted = lambda: True
        new_data_access_request.save()
        mock_stop_environments_with_expired_access.assert_not_called()

    @patch("environment.signals.stop_environments_with_expired_access")
    @patch("environment.signals.user_has_billing_setup")
    def test_does_not_schedule_task_on_save_if_access_duration_was_not_specified(
        self, mock_user_has_billing_setup, mock_stop_environments_with_expired_access
    ):
        mock_user_has_billing_setup.return_value = True
        requester = User()
        requester.save()
        new_data_access_request = DataAccessRequest(requester=requester, project_id=1)
        new_data_access_request._original_is_accepted = False
        new_data_access_request.is_accepted = lambda: True
        new_data_access_request.save()
        mock_stop_environments_with_expired_access.assert_not_called()

    @patch("environment.signals.stop_environments_with_expired_access")
    @patch("environment.signals.user_has_billing_setup")
    def test_schedules_task_on_save_if_request_with_duration_was_accepted(
        self, mock_user_has_billing_setup, mock_stop_environments_with_expired_access
    ):
        mock_user_has_billing_setup.return_value = True
        requester = User()
        requester.save()
        new_data_access_request = DataAccessRequest(
            requester=requester, project_id=1, duration=timedelta(days=10)
        )
        new_data_access_request._original_is_accepted = False
        new_data_access_request.is_accepted = lambda: True
        new_data_access_request.save()
        mock_stop_environments_with_expired_access.assert_called()

    @patch("environment.signals.stop_environments_with_expired_access")
    @patch("environment.signals.user_has_billing_setup")
    def test_schedules_task_on_save_if_access_was_revoked(
        self, mock_user_has_billing_setup, mock_stop_environments_with_expired_access
    ):
        mock_user_has_billing_setup.return_value = True
        requester = User()
        requester.save()
        new_data_access_request = DataAccessRequest(requester=requester, project_id=1)
        new_data_access_request._original_is_revoked = False
        new_data_access_request.is_revoked = lambda: True
        new_data_access_request.save()
        mock_stop_environments_with_expired_access.assert_called()
