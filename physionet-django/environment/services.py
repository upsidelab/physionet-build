from typing import Tuple, Iterable, Optional, Callable

from django.db.models import Q, Model
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
from google.cloud.workflows import executions_v1beta
from google.cloud.workflows.executions_v1beta.types import executions

import environment.api as api
from environment.models import CloudIdentity, BillingSetup, Workflow
from environment.exceptions import (
    IdentityProvisioningFailed,
    StopEnvironmentFailed,
    StartEnvironmentFailed,
    DeleteEnvironmentFailed,
    ChangeEnvironmentInstanceTypeFailed,
    BillingVerificationFailed,
    EnvironmentCreationFailed,
    GetAvailableEnvironmentsFailed,
    GetWorkspaceDetailsFailed,
    GetUserInfoFailed,
)
from environment.deserializers import (
    deserialize_research_environments,
    deserialize_workspace_details,
)
from environment.entities import (
    ResearchEnvironment,
    InstanceType,
    Region,
    ResearchWorkspace,
)
from environment.utilities import left_join_iterators, inner_join_iterators
from project.models import AccessPolicy, PublishedProject


User = Model

DEFAULT_REGION = "us-central1"


def _project_data_group(project: PublishedProject) -> str:
    return project.dataaccesss.get(platform=5).location


def _environment_data_group(environment: ResearchEnvironment) -> str:
    return environment.group_granting_data_access


def create_cloud_identity(user: User) -> Tuple[str, CloudIdentity]:
    gcp_user_id = user.username
    response = api.create_cloud_identity(
        gcp_user_id, user.profile.first_names, user.profile.last_name
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise IdentityProvisioningFailed(error_message)

    body = response.json()
    identity = CloudIdentity.objects.create(
        user=user, gcp_user_id=gcp_user_id, email=body["email-id"]
    )
    otp = body["one-time-password"]
    return otp, identity


def get_user_info(user: User):
    response = api.get_user_info(gcp_user_id=user.username)

    if (
        not response.ok
    ):  # right now response form API is always ok (maybe except Runtime)
        error_message = response.json()["message"]
        raise GetUserInfoFailed(error_message)

    return response.json()


def verify_billing_and_create_workspace(user: User, billing_id: str):
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.create_workspace(
        gcp_user_id=gcp_user_id,
        billing_id=billing_id,
        region=DEFAULT_REGION,
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
        "group_granting_data_access": _project_data_group(project),
        "persistent_disk": str(persistent_disk),
    }
    if environment_type == "jupyter":
        jupyter_kwargs = {
            "vm_image": "common-cpu-notebooks",
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
) -> str:
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
        error_message = response.json()[
            "error"
        ]  # TODO: Check all uses of "error"/"message"
        raise EnvironmentCreationFailed(error_message)

    execution_resource_name = response.json()["execution-name"]
    persist_workflow(
        user=user,
        execution_resource_name=execution_resource_name,
        project_id=project.pk,
        type=Workflow.CREATE,
    )

    return response.json()


def get_workspace_details(user: User, region: Region) -> ResearchWorkspace:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.get_workspace_details(
        gcp_user_id=gcp_user_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["error"]
        raise GetWorkspaceDetailsFailed(error_message)

    research_workspace = deserialize_workspace_details(response.json())
    return research_workspace


def is_user_workspace_setup_done(user: User) -> bool:
    try:
        workspace = get_workspace_details(user, Region(DEFAULT_REGION))
        return workspace.setup_finished
    except GetWorkspaceDetailsFailed:
        return False


def mark_user_workspace_setup_as_done(user: User):
    cloud_identity = user.cloud_identity
    cloud_identity.initial_workspace_setup_done = True
    cloud_identity.save()


def get_available_projects(user: User) -> Iterable[PublishedProject]:
    data_access_filters = Q(dataaccesss__platform=5)
    access_policy_filters = Q(access_policy=AccessPolicy.OPEN) | Q(
        access_policy=AccessPolicy.RESTRICTED
    )
    if user.is_credentialed:
        access_policy_filters = access_policy_filters | Q(
            access_policy=AccessPolicy.CREDENTIALED
        )
    return PublishedProject.objects.prefetch_related("workflows").filter(
        data_access_filters & access_policy_filters
    )


def _get_projects_for_environments(
    environments: Iterable[ResearchEnvironment],
) -> Iterable[PublishedProject]:
    group_granting_data_accesses = map(_environment_data_group, environments)
    return PublishedProject.objects.filter(
        dataaccesss__platform=5, dataaccesss__location__in=group_granting_data_accesses
    )


def get_environments_with_projects(
    user: User,
) -> Iterable[Tuple[ResearchEnvironment, PublishedProject, Iterable[Workflow]]]:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.get_workspace_list(gcp_user_id)
    if not response.ok:
        error_message = response.json()["error"]
        raise GetAvailableEnvironmentsFailed(error_message)
    all_environments = deserialize_research_environments(response.json())
    active_environments = [
        environment for environment in all_environments if environment.is_active
    ]
    projects = _get_projects_for_environments(active_environments)
    environment_project_pairs = inner_join_iterators(
        _environment_data_group, active_environments, _project_data_group, projects
    )
    return [
        (environment, project, project.workflows.in_progress().filter(user=user))
        for environment, project in environment_project_pairs
    ]


def get_available_projects_with_environments(
    user: User,
    environments: Iterable[ResearchEnvironment],
) -> Iterable[
    Tuple[PublishedProject, Optional[ResearchEnvironment], Iterable[Workflow]]
]:
    available_projects = get_available_projects(user)
    project_environment_pairs = left_join_iterators(
        _project_data_group,
        available_projects,
        _environment_data_group,
        environments,
    )
    return [
        (project, environment, project.workflows.in_progress().filter(user=user))
        for project, environment in project_environment_pairs
    ]


def get_projects_with_environment_being_created(
    project_environment_workflow_triplets: Iterable[
        Tuple[PublishedProject, Optional[ResearchEnvironment], Iterable[Workflow]]
    ],
) -> Iterable[Tuple[None, PublishedProject, Iterable[Workflow]]]:
    return [
        (environment, project, workflows)
        for project, environment, workflows in project_environment_workflow_triplets
        if environment is None and project.workflows.exists()
    ]


def get_environment_project_pairs_with_expired_access(
    user: User,
) -> Iterable[Tuple[ResearchEnvironment, PublishedProject]]:
    all_environment_project_pairs = get_environments_with_projects(user)
    return [
        (environment, project)
        for environment, project in all_environment_project_pairs
        if not project.has_access(user)
    ]


def stop_running_environment(
    user: User, project_id: str, workbench_id: str, region: Region
) -> str:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.stop_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["error"]
        raise StopEnvironmentFailed(error_message)

    execution_resource_name = response.json()["execution-name"]
    persist_workflow(
        user=user,
        execution_resource_name=execution_resource_name,
        project_id=project_id,
        type=Workflow.PAUSE,
    )

    return response.json()


def start_stopped_environment(
    user: User, project_id: str, workbench_id: str, region: Region
) -> str:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.start_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise StartEnvironmentFailed(error_message)

    execution_resource_name = response.json()["execution-name"]
    persist_workflow(
        user=user,
        execution_resource_name=execution_resource_name,
        project_id=project_id,
        type=Workflow.START,
    )

    return response.json()


def change_environment_instance_type(
    user: User,
    project_id: str,
    workbench_id: str,
    region: Region,
    new_instance_type: InstanceType,
) -> str:
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

    execution_resource_name = response.json()["execution-name"]
    persist_workflow(
        user=user,
        execution_resource_name=execution_resource_name,
        project_id=project_id,
        type=Workflow.CHANGE,
    )

    return response.json()


def delete_environment(
    user: User, project_id: str, workbench_id: str, region: Region
) -> str:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.delete_workbench(
        gcp_user_id=gcp_user_id,
        workbench_id=workbench_id,
        region=region.value,
    )
    if not response.ok:
        error_message = response.json()["message"]
        raise DeleteEnvironmentFailed(error_message)

    execution_resource_name = response.json()["execution-name"]
    persist_workflow(
        user=user,
        execution_resource_name=execution_resource_name,
        project_id=project_id,
        type=Workflow.DESTROY,
    )

    return response.json()


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


def persist_workflow(
    user: User, execution_resource_name: str, project_id: int, type: int
) -> Workflow:
    return Workflow.objects.create(
        user=user,
        execution_resource_name=execution_resource_name,
        project_id=project_id,
        type=type,
        status=Workflow.INPROGRESS,
    )


def get_execution_state_closure() -> Callable[[str], executions.Execution.State]:
    client = executions_v1beta.ExecutionsClient()

    def wrapper(execution_resource_name: str) -> bool:
        execution = client.get_execution(request={"name": execution_resource_name})
        return execution.state

    return wrapper


get_execution_state = get_execution_state_closure()


def mark_workflow_as_finished(
    execution_resource_name: str, execution_state: executions.Execution.State
):
    workflow = Workflow.objects.get(execution_resource_name=execution_resource_name)
    if execution_state == executions.Execution.State.SUCCEEDED:
        workflow.status = Workflow.SUCCESS
    else:
        workflow.status = Workflow.FAILED

    workflow.save()
