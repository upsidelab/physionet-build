from typing import Tuple, Iterable, Optional

from django.db.models import Q, Model
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings

import environment.api as api
from environment.models import CloudIdentity, BillingSetup
from environment.exceptions import (
    IdentityProvisioningFailed,
    StopEnvironmentFailed,
    StartEnvironmentFailed,
    DeleteEnvironmentFailed,
    ChangeEnvironmentInstanceTypeFailed,
    BillingVerificationFailed,
    EnvironmentCreationFailed,
    GetAvailableEnvironmentsFailed,
)
from environment.deserializers import deserialize_research_environments
from environment.entities import (
    ResearchEnvironment,
    InstanceType,
    Region,
)
from environment.utilities import left_join_iterators, inner_join_iterators
from project.models import AccessPolicy, PublishedProject


User = Model


def _project_dataset(project: PublishedProject) -> str:
    return project.dataaccesss.get(platform=5).location


def _environment_dataset(environment: ResearchEnvironment) -> str:
    return environment.dataset


def create_cloud_identity(user: User) -> Tuple[str, CloudIdentity]:
    response = api.create_cloud_identity(
        f"researcher.{user.username}", user.profile.first_names, user.profile.last_name
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise IdentityProvisioningFailed(error_message)

    body = response.json()
    identity = CloudIdentity.objects.create(
        user=user, gcp_user_id=f"researcher.{user.username}", email=body["email-id"]
    )
    otp = body["one-time-password"]
    return otp, identity


def verify_billing_and_create_workspace(user: User, billing_id: str):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.create_workspace(
        gcp_user_id=gcp_user_id,
        billing_id=billing_id,
        region="us-central1",  # FIXME: Temporary hardcoded
    )
    if not response.ok:
        error_message = response.json()["error"]
        raise BillingVerificationFailed(error_message)


def create_billing_setup(user: User, billing_account_id: str) -> BillingSetup:
    cloud_identity = user.cloud_identity
    billing_setup = BillingSetup.objects.create(
        cloud_identity=cloud_identity, billing_account_id=billing_account_id
    )
    return billing_setup


def _create_workbench_kwargs(
    user: User,
    project: PublishedProject,
    region: str,
    instance_type: str,
    environment_type: str,
    persistent_disk: Optional[int],
) -> dict:
    gcp_user_id = user.cloud_identity.gcp_user_id

    common = {
        "gcp_user_id": gcp_user_id,
        "region": region,
        "environment_type": environment_type,
        "instance_type": instance_type,
        "dataset": _project_dataset(
            project
        ),  # FIXME: Dashes in the name are not accepted by the API
    }
    if environment_type == "jupyter":
        jupyter_kwargs = {
            "vm_image": "common-cpu-notebooks",
            "persistent_disk": str(persistent_disk),
            "bucket_name": project.project_file_root(),
        }
        return {**common, **jupyter_kwargs}
    else:
        return common


def create_research_environment(
    user: User,
    project: PublishedProject,
    region: str,
    instance_type: str,
    environment_type: str,
    persistent_disk: Optional[int],
):
    kwargs = _create_workbench_kwargs(
        user,
        project,
        region,
        instance_type,
        environment_type,
        persistent_disk,
    )
    response = api.create_workbench(**kwargs)
    if not response.ok:
        error_message = response.json()["error"]
        raise EnvironmentCreationFailed(error_message)

    return response


def get_available_projects(user: User) -> Iterable[PublishedProject]:
    data_access_filters = Q(dataaccesss__platform=5)
    access_policy_filters = Q(access_policy=AccessPolicy.OPEN) | Q(
        access_policy=AccessPolicy.RESTRICTED
    )
    if user.is_credentialed:
        access_policy_filters = access_policy_filters | Q(
            access_policy=AccessPolicy.CREDENTIALED
        )
    return PublishedProject.objects.filter(data_access_filters & access_policy_filters)


def _get_projects_for_environments(
    environments: Iterable[ResearchEnvironment],
) -> Iterable[PublishedProject]:
    datasets = map(_environment_dataset, environments)
    return PublishedProject.objects.filter(
        dataaccesss__platform=5, dataaccesss__location__in=datasets
    )


def get_environments_with_projects(
    user: User,
) -> Iterable[Tuple[ResearchEnvironment, PublishedProject]]:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.get_workspace_list(gcp_user_id)
    if not response.ok:
        error_message = response.json()["error"]
        raise GetAvailableEnvironmentsFailed(error_message)
    all_environments = deserialize_research_environments(response.json())
    active_environments = [
        environment
        for environment in all_environments
        if environment.is_running or environment.is_paused
    ]
    projects = _get_projects_for_environments(active_environments)
    environment_project_pairs = inner_join_iterators(  # TODO: Consider left join as this will preserve environments for deleted projects
        _environment_dataset, active_environments, _project_dataset, projects
    )

    return environment_project_pairs


def get_available_projects_with_environments(
    user: User,
    environments: Iterable[ResearchEnvironment],
) -> Iterable[Tuple[PublishedProject, Optional[ResearchEnvironment]]]:
    available_projects = get_available_projects(user)
    return left_join_iterators(
        _project_dataset,
        available_projects,
        _environment_dataset,
        environments,
    )


def get_environment_project_pairs_with_expired_access(
    user: User,
) -> Iterable[Tuple[ResearchEnvironment, PublishedProject]]:
    all_environment_project_pairs = get_environments_with_projects(user)
    return [
        (environment, project)
        for environment, project in all_environment_project_pairs
        if not project.has_access(user)
    ]


def stop_running_environment(user: User, workbench_id: str, region: Region):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.stop_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["error"]
        raise StopEnvironmentFailed(error_message)
    return response


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
    return response


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
    return response


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
    return response


def send_environment_access_expired_email(
    user: User, projects: Iterable[PublishedProject]
):
    subject = f"{settings.SITE_NAME} Environment Access Expired"
    email_context = {
        "signature": settings.EMAIL_SIGNATURE,
        "projects": projects,
    }
    body = loader.render_to_string(
        "environment/email/environment_access_expired.html", email_context
    )
    send_mail(
        subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False
    )
