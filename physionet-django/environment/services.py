from typing import Tuple, Iterable, Optional

from django.db.models import Q

import environment.api as api
from environment.models import CloudIdentity, BillingSetup
from environment.exceptions import (
    IdentityProvisioningFailed,
    StopEnvironmentFailed,
    StartEnvironmentFailed,
    DeleteEnvironmentFailed,
    ChangeEnvironmentInstanceTypeFailed,
)
from environment.deserializers import deserialize_research_environments
from environment.entities import (
    ResearchEnvironment,
    EnvironmentStatus,
    InstanceType,
    Region,
)
from user.models import User
from project.models import AccessPolicy, PublishedProject


def create_cloud_identity(user: User) -> Tuple[str, CloudIdentity]:
    response = api.create_cloud_identity(
        user.username, user.profile.first_names, user.profile.last_name
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise IdentityProvisioningFailed(error_message)

    body = response.json()
    identity = CloudIdentity.objects.create(
        user=user, gcp_user_id=user.username, email=body["email-id"]
    )
    otp = body["one-time-password"]
    return otp, identity


def create_billing_setup(user: User, billing_account_id: str) -> BillingSetup:
    cloud_identity = user.cloud_identity
    billing_setup = BillingSetup.objects.create(
        cloud_identity=cloud_identity, billing_account_id=billing_account_id
    )
    return billing_setup


def get_available_projects(user: User) -> Iterable[PublishedProject]:
    version_filters = Q(
        is_latest_version=True
    )  # TODO: Add support for non-latest versions
    access_policy_filters = Q(access_policy=AccessPolicy.OPEN) | Q(
        access_policy=AccessPolicy.RESTRICTED
    )
    if user.is_credentialed:
        access_policy_filters = access_policy_filters | Q(
            access_policy=AccessPolicy.CREDENTIALED
        )
    return PublishedProject.objects.filter(version_filters & access_policy_filters)


def get_available_environments(user: User) -> Iterable[ResearchEnvironment]:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.get_workspace_list(gcp_user_id)
    all_environments = deserialize_research_environments(response.json())
    running_environments = [
        environment
        for environment in all_environments
        if environment.status is not EnvironmentStatus.DESTROYED
    ]

    return running_environments


def match_projects_with_environments(
    projects: Iterable[PublishedProject], environments: Iterable[ResearchEnvironment]
) -> Iterable[Tuple[PublishedProject, Optional[ResearchEnvironment]]]:
    return [
        (
            project,
            next(
                filter(
                    lambda environment: project.slug == environment.dataset,
                    environments,
                ),
                None,
            ),
        )
        for project in projects
    ]


def stop_running_environment(user: User, workbench_id: str, region: Region):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.stop_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise StopEnvironmentFailed(error_message)


def start_stopped_environment(user: User, workbench_id: str, region: Region):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.start_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise StartEnvironmentFailed(error_message)


def change_environment_instance_type(
    user: User,
    workbench_id: str,
    region: Region,
    new_instance_type: InstanceType,
):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.change_workbench_instance_type(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
        new_instance_type=new_instance_type.value,
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise ChangeEnvironmentInstanceTypeFailed(error_message)


def delete_environment(user: User, workbench_id: str, region: Region):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.delete_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise DeleteEnvironmentFailed(error_message)
