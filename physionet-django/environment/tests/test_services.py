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
)
from environment.exceptions import (
    IdentityProvisioningFailed,
    EnvironmentCreationFailed,
    StopEnvironmentFailed,
    StartEnvironmentFailed,
    ChangeEnvironmentInstanceTypeFailed,
    DeleteEnvironmentFailed,
)
from environment.models import CloudIdentity, BillingSetup
from environment.entities import Region, InstanceType


User = get_user_model()


@skipIf(not settings.ENABLE_RESEARCH_ENVIRONMENTS, "Research environments are disabled")
class CreateCloudIdentityTestCase(TestCase):
    def setUp(self):
        self.user_without_cloud_identity = User.objects.create_user("foo", "bar", "baz")

    @patch("environment.api.create_cloud_identity")
    def test_raises_if_request_fails(self, mock_create_cloud_identity):
        mock_create_cloud_identity.return_value.ok = False
        self.assertRaises(
            IdentityProvisioningFailed,
            create_cloud_identity,
            self.user_without_cloud_identity,
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

        otp, identity = create_cloud_identity(self.user_without_cloud_identity)
        self.assertEqual(otp, mock_otp)
        self.assertEqual(
            identity.gcp_user_id, self.user_without_cloud_identity.username
        )
        self.assertEqual(identity.email, mock_email)
        self.assertEqual(self.user_without_cloud_identity.cloud_identity, identity)


class CreateBillingSetupTestCase(TestCase):
    def setUp(self):
        self.user_without_billing_setup = User.objects.create_user("foo", "bar", "baz")
        CloudIdentity.objects.create(
            user=self.user_without_billing_setup,
            gcp_user_id=self.user_without_billing_setup.username,
            email=self.user_without_billing_setup.email,
        )

    def test_creates_billing_setup_for_specified_user(self):
        mock_billing_account = "XXXXXX-XXXXXX-XXXXXX"
        billing_setup = create_billing_setup(
            self.user_without_billing_setup, mock_billing_account
        )
        self.assertEqual(
            self.user_without_billing_setup.cloud_identity.billing_setup, billing_setup
        )
        self.assertEqual(billing_setup.billing_account_id, mock_billing_account)


class CreateResearchEnvironmentTestCase(TestCase):
    def setUp(self):
        self.project = MagicMock()
        self.project.slug = "slug"
        self.project.get_project_file_root.return_value = "bucket"
        self.user = User.objects.create_user("foo", "bar", "baz")
        cloud_identity = CloudIdentity.objects.create(
            user=self.user,
            gcp_user_id=self.user.username,
            email=self.user.email,
        )
        BillingSetup.objects.create(
            cloud_identity=cloud_identity, billing_account_id="XXXXXX-XXXXXX-XXXXXX"
        )

    @patch("environment.api.create_workbench")
    def test_raises_if_request_fails(self, mock_create_research_environment):
        mock_create_research_environment.return_value.ok = False
        self.assertRaises(
            EnvironmentCreationFailed,
            create_research_environment,
            self.user,
            self.project,
            "region",
            "instance_type",
            "enviornment_type",
        )

    @patch("environment.api.create_workbench")
    def test_returns_api_response_if_request_succeeds(self, mock_create_workbench):
        mock_create_workbench.return_value.ok = True
        result = create_research_environment(
            self.user,
            self.project,
            "region",
            "instance_type",
            "enviornment_type",
        )
        self.assertEqual(result, mock_create_workbench.return_value)


class StopRunningEnvironmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("foo", "bar", "baz")
        cloud_identity = CloudIdentity.objects.create(
            user=self.user,
            gcp_user_id=self.user.username,
            email=self.user.email,
        )
        BillingSetup.objects.create(
            cloud_identity=cloud_identity, billing_account_id="XXXXXX-XXXXXX-XXXXXX"
        )

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
    def test_raises_if_request_fails(self, mock_stop_workbench):
        mock_stop_workbench.return_value.ok = True
        result = stop_running_environment(
            self.user, "workbench_id", Region.AUSTRALIA_SOUTHEAST
        )
        self.assertEqual(result, mock_stop_workbench.return_value)


class StartStoppedEnvironmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("foo", "bar", "baz")
        cloud_identity = CloudIdentity.objects.create(
            user=self.user,
            gcp_user_id=self.user.username,
            email=self.user.email,
        )
        BillingSetup.objects.create(
            cloud_identity=cloud_identity, billing_account_id="XXXXXX-XXXXXX-XXXXXX"
        )

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
    def test_raises_if_request_fails(self, mock_stop_workbench):
        mock_stop_workbench.return_value.ok = True
        result = start_stopped_environment(
            self.user, "workbench_id", Region.AUSTRALIA_SOUTHEAST
        )
        self.assertEqual(result, mock_stop_workbench.return_value)


class ChangeEnvironmentInstanceTypeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("foo", "bar", "baz")
        cloud_identity = CloudIdentity.objects.create(
            user=self.user,
            gcp_user_id=self.user.username,
            email=self.user.email,
        )
        BillingSetup.objects.create(
            cloud_identity=cloud_identity, billing_account_id="XXXXXX-XXXXXX-XXXXXX"
        )

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
    def test_raises_if_request_fails(self, mock_change_workbench_instance_type):
        mock_change_workbench_instance_type.return_value.ok = True
        result = change_environment_instance_type(
            self.user,
            "workbench_id",
            Region.AUSTRALIA_SOUTHEAST,
            InstanceType.N1_STANDARD_1,
        )
        self.assertEqual(result, mock_change_workbench_instance_type.return_value)


class DeleteEnvironmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("foo", "bar", "baz")
        cloud_identity = CloudIdentity.objects.create(
            user=self.user,
            gcp_user_id=self.user.username,
            email=self.user.email,
        )
        BillingSetup.objects.create(
            cloud_identity=cloud_identity, billing_account_id="XXXXXX-XXXXXX-XXXXXX"
        )

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
    def test_raises_if_request_fails(self, mock_delete_workbench):
        mock_delete_workbench.return_value.ok = True
        result = delete_environment(
            self.user, "workbench_id", Region.AUSTRALIA_SOUTHEAST
        )
        self.assertEqual(result, mock_delete_workbench.return_value)
