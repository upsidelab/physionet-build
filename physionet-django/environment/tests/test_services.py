from unittest import skipIf
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model

from environment.services import (
    create_cloud_identity,
    create_billing_setup,
    create_research_environment,
    stop_running_environment,
    start_stopped_environment,
    change_environment_instance_type,
    delete_environment,
    verify_billing_and_create_workspace,
    get_available_environments,
)
from environment.exceptions import (
    IdentityProvisioningFailed,
    EnvironmentCreationFailed,
    StopEnvironmentFailed,
    StartEnvironmentFailed,
    ChangeEnvironmentInstanceTypeFailed,
    DeleteEnvironmentFailed,
    BillingVerificationFailed,
    GetAvailableEnvironmentsFailed,
)
from environment.entities import (
    Region,
    InstanceType,
    EnvironmentStatus,
    ResearchEnvironment,
)
from environment.tests.mocks import get_workspace_list_json
from environment.tests.helpers import (
    create_user_without_cloud_identity,
    create_user_with_cloud_identity,
    create_user_with_billing_setup,
)

User = get_user_model()


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class CreateCloudIdentityTestCase(TestCase):
    def setUp(self):
        self.user = create_user_without_cloud_identity()

    @patch("environment.api.create_cloud_identity")
    def test_raises_if_request_fails(self, mock_create_cloud_identity):
        mock_create_cloud_identity.return_value.ok = False
        self.assertRaises(
            IdentityProvisioningFailed,
            create_cloud_identity,
            self.user,
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

        otp, identity = create_cloud_identity(self.user)
        self.assertEqual(otp, mock_otp)
        self.assertEqual(identity.gcp_user_id, f"researcher.{self.user.username}")
        self.assertEqual(identity.email, mock_email)
        self.assertEqual(self.user.cloud_identity, identity)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class CreateBillingSetupTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_cloud_identity()

    def test_creates_billing_setup_for_specified_user(self):
        mock_billing_account = "XXXXXX-XXXXXX-XXXXXX"
        billing_setup = create_billing_setup(self.user, mock_billing_account)
        self.assertEqual(self.user.cloud_identity.billing_setup, billing_setup)
        self.assertEqual(billing_setup.billing_account_id, mock_billing_account)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class CreateResearchEnvironmentTestCase(TestCase):
    def setUp(self):
        self.project = MagicMock()
        self.project.slug = "slug"
        self.project.get_project_file_root.return_value = "bucket"
        self.user = create_user_with_billing_setup()

    @patch("environment.api.create_workbench")
    def test_raises_if_request_fails(self, mock_create_workbench):
        mock_create_workbench.return_value.ok = False
        self.assertRaises(
            EnvironmentCreationFailed,
            create_research_environment,
            self.user,
            self.project,
            "us-central1",
            "n1-standard-1",
            "enviornment_type",
            "100",
        )

    @patch("environment.api.create_workbench")
    def test_returns_api_response_if_request_succeeds(self, mock_create_workbench):
        mock_create_workbench.return_value.ok = True
        result = create_research_environment(
            self.user,
            self.project,
            "us-central1",
            "n1-standard-1",
            "enviornment_type",
            "100",
        )
        self.assertEqual(result, mock_create_workbench.return_value)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class StopRunningEnvironmentTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_billing_setup()

    @patch("environment.api.stop_workbench")
    def test_raises_if_request_fails(self, mock_stop_workbench):
        mock_stop_workbench.return_value.ok = False
        self.assertRaises(
            StopEnvironmentFailed,
            stop_running_environment,
            self.user,
            "workbench_id",
            Region.AUSTRALIA_SOUTHEAST,
        )

    @patch("environment.api.stop_workbench")
    def test_raises_if_request_succeeds(self, mock_stop_workbench):
        mock_stop_workbench.return_value.ok = True
        result = stop_running_environment(
            self.user, "workbench_id", Region.AUSTRALIA_SOUTHEAST
        )
        self.assertEqual(result, mock_stop_workbench.return_value)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class StartStoppedEnvironmentTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_billing_setup()

    @patch("environment.api.start_workbench")
    def test_raises_if_request_fails(self, mock_start_workbench):
        mock_start_workbench.return_value.ok = False
        self.assertRaises(
            StartEnvironmentFailed,
            start_stopped_environment,
            self.user,
            "workbench_id",
            Region.AUSTRALIA_SOUTHEAST,
        )

    @patch("environment.api.start_workbench")
    def test_raises_if_request_succeeds(self, mock_stop_workbench):
        mock_stop_workbench.return_value.ok = True
        result = start_stopped_environment(
            self.user, "workbench_id", Region.AUSTRALIA_SOUTHEAST
        )
        self.assertEqual(result, mock_stop_workbench.return_value)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class ChangeEnvironmentInstanceTypeTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_billing_setup()

    @patch("environment.api.change_workbench_instance_type")
    def test_raises_if_request_fails(self, mock_change_workbench_instance_type):
        mock_change_workbench_instance_type.return_value.ok = False
        self.assertRaises(
            ChangeEnvironmentInstanceTypeFailed,
            change_environment_instance_type,
            self.user,
            "workbench_id",
            Region.AUSTRALIA_SOUTHEAST,
            InstanceType.N1_STANDARD_1,
        )

    @patch("environment.api.change_workbench_instance_type")
    def test_raises_if_request_succeeds(self, mock_change_workbench_instance_type):
        mock_change_workbench_instance_type.return_value.ok = True
        result = change_environment_instance_type(
            self.user,
            "workbench_id",
            Region.AUSTRALIA_SOUTHEAST,
            InstanceType.N1_STANDARD_1,
        )
        self.assertEqual(result, mock_change_workbench_instance_type.return_value)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class DeleteEnvironmentTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_billing_setup()

    @patch("environment.api.delete_workbench")
    def test_raises_if_request_fails(self, mock_delete_workbench):
        mock_delete_workbench.return_value.ok = False
        self.assertRaises(
            DeleteEnvironmentFailed,
            delete_environment,
            self.user,
            "workbench_id",
            Region.AUSTRALIA_SOUTHEAST,
        )

    @patch("environment.api.delete_workbench")
    def test_raises_if_request_succeeds(self, mock_delete_workbench):
        mock_delete_workbench.return_value.ok = True
        result = delete_environment(
            self.user, "workbench_id", Region.AUSTRALIA_SOUTHEAST
        )
        self.assertEqual(result, mock_delete_workbench.return_value)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class VerifyBillingAndCreateWorkspaceTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_cloud_identity()
        self.some_billing_id = "XXXXXX-XXXXXX-XXXXXX"

    @patch("environment.api.create_workspace")
    def test_raises_if_request_fails(self, mock_create_workspace):
        mock_create_workspace.return_value.ok = False
        self.assertRaises(
            BillingVerificationFailed,
            verify_billing_and_create_workspace,
            self.user,
            self.some_billing_id,
        )

    @patch("environment.api.create_workspace")
    def test_not_raises_if_request_succeeds(self, mock_create_workspace):
        mock_create_workspace.return_value.ok = True
        verify_billing_and_create_workspace(self.user, self.some_billing_id)


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class GetAvailableEnvironmentsTestCase(TestCase):
    def setUp(self):
        self.user = create_user_with_cloud_identity()

    @patch("environment.api.get_workspace_list")
    def test_get_running_environments_succeed(self, mock_get_workspace_list):
        mock_get_workspace_list.return_value.json.return_value = get_workspace_list_json

        running_environments = get_available_environments(self.user)

        self.assertTrue(
            all(
                True if environment.status != EnvironmentStatus.DESTROYED else False
                for environment in running_environments
            )
        )
        self.assertIsInstance(running_environments, list)
        self.assertTrue(
            all(
                True if isinstance(environment, ResearchEnvironment) else False
                for environment in running_environments
            )
        )

    @patch("environment.api.get_workspace_list")
    def test_raises_if_request_fails(self, mock_get_workspace_list):
        mock_get_workspace_list.return_value.ok = False
        self.assertRaises(
            GetAvailableEnvironmentsFailed, get_available_environments, self.user
        )
