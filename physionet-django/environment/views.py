import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET

import environment.services as services
from environment.forms import BillingAccountIdForm, CreateResearchEnvironmentForm
from environment.exceptions import BillingVerificationFailed
from environment.decorators import (
    cloud_identity_required,
    billing_setup_required,
    workspace_setup_required,
    require_DELETE,
    require_PATCH,
)
from environment.entities import Region, InstanceType
from environment.utilities import (
    user_has_cloud_identity,
    user_has_billing_setup,
)
from environment.models import Workflow


@require_http_methods(["GET", "POST"])
@login_required
def identity_provisioning(request):
    # assuming that if user has could_identity => user has cloud_identity in API
    if user_has_cloud_identity(request.user):
        return redirect("billing_setup")

    # user has no cloud identity, and now we check if he has cloud identity in API
    user_info = services.get_user_info(request.user)
    if user_info.get("user-status") == "user-added-in-cloud-identity":
        _identity = services.create_cloud_identity_object(
            user=request.user,
            gcp_user_id=user_info.get("user-id"),
            email=user_info.get("email"),
        )
        return redirect("billing_setup")

    if request.method == "POST":
        otp, _ = services.create_cloud_identity(request.user)
        request.session["cloud_identity_otp"] = otp
        return redirect("billing_setup")

    return render(request, "environment/identity_provisioning.html")


@require_http_methods(["GET", "POST"])
@login_required
@cloud_identity_required
def billing_setup(request):
    if user_has_billing_setup(request.user):
        return redirect("research_environments")

    if request.method == "POST":
        form = BillingAccountIdForm(request.POST)
        if form.is_valid():
            try:
                services.verify_billing_and_create_workspace(
                    user=request.user,
                    billing_id=form.cleaned_data["billing_account_id"],
                )
                services.create_billing_setup(
                    request.user, form.cleaned_data["billing_account_id"]
                )
                return redirect("research_environments")
            except BillingVerificationFailed as err:
                form.add_error("billing_account_id", err)
    else:
        form = BillingAccountIdForm()

    cloud_identity = request.user.cloud_identity
    context = {
        "email": cloud_identity.email,
        "otp": request.session.get("cloud_identity_otp"),
        "form": form,
    }
    return render(request, "environment/billing_setup.html", context)


@require_GET
@login_required
@cloud_identity_required
@billing_setup_required
def workspace_setup(request):
    if request.user.cloud_identity.initial_workspace_setup_done:
        return redirect("research_environments")

    is_workspace_done = services.is_user_workspace_setup_done(request.user)
    if not is_workspace_done:
        return render(request, "environment/workspace_being_provisioned.html")
    services.mark_user_workspace_setup_as_done(request.user)
    return redirect("research_environments")


@require_GET
@login_required
@cloud_identity_required
@billing_setup_required
@workspace_setup_required
def research_environments(request):
    environment_project_pairs = services.get_environments_with_projects(request.user)
    environments = map(lambda pair: pair[0], environment_project_pairs)
    available_project_environment_pairs = (
        services.get_available_projects_with_environments(
            request.user,
            environments,
        )
    )
    context = {
        "environment_project_pairs": environment_project_pairs,
        # An environment may be running for an unavailable project
        "available_project_environment_pairs": available_project_environment_pairs,
        # Available projects with info whether it has an environment
        "cloud_identity": request.user.cloud_identity,
    }
    return render(
        request,
        "environment/research_environments.html",
        context,
    )


@require_GET
@login_required
@cloud_identity_required
@billing_setup_required
@workspace_setup_required
def research_environments_partial(request):
    environment_project_pairs = services.get_environments_with_projects(request.user)
    context = {"environment_project_pairs": environment_project_pairs}
    return render(
        request,
        "environment/_available_environments_list.html",
        context,
    )


@require_http_methods(["GET", "POST"])
@login_required
@cloud_identity_required
@billing_setup_required
def create_research_environment(request, project_slug, project_version):
    project = services.get_available_projects(request.user).get(
        slug=project_slug, version=project_version
    )

    if request.method == "POST":
        form = CreateResearchEnvironmentForm(request.POST)
        if form.is_valid():
            execution_resource_name = services.create_research_environment(
                user=request.user,
                project=project,
                region=form.cleaned_data["region"],
                instance_type=form.cleaned_data["instance_type"],
                environment_type=form.cleaned_data["environment_type"],
                persistent_disk=form.cleaned_data.get("persistent_disk"),
            )
            services.persist_workflow(
                execution_resource_name=execution_resource_name,
                project_id=project.pk,
                type=Workflow.CREATE,
            )
            return redirect("research_environments")
    else:
        form = CreateResearchEnvironmentForm()

    context = {"form": form, "project": project}
    return render(request, "environment/create_research_environment.html", context)


@require_PATCH
@login_required
@cloud_identity_required
@billing_setup_required
def stop_running_environment(request):
    data = json.loads(request.body)
    execution_resource_name = services.stop_running_environment(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
    )
    services.persist_workflow(
        execution_resource_name=execution_resource_name,
        project_id=data["project_id"],
        type=Workflow.PAUSE,
    )
    return JsonResponse({})


@require_PATCH
@login_required
@cloud_identity_required
@billing_setup_required
def start_stopped_environment(request):
    data = json.loads(request.body)
    execution_resource_name = services.start_stopped_environment(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
    )
    services.persist_workflow(
        execution_resource_name=execution_resource_name,
        project_id=data["project_id"],
        type=Workflow.START,
    )
    return JsonResponse({})


@require_PATCH
@login_required
@cloud_identity_required
@billing_setup_required
def change_environment_instance_type(request):
    data = json.loads(request.body)
    execution_resource_name = services.change_environment_instance_type(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
        new_instance_type=InstanceType(data["instance_type"]),
    )
    services.persist_workflow(
        execution_resource_name=execution_resource_name,
        project_id=data["project_id"],
        type=Workflow.CHANGE,
    )
    return JsonResponse({})


@require_DELETE
@login_required
@cloud_identity_required
@billing_setup_required
def delete_environment(request):
    data = json.loads(request.body)
    execution_resource_name = services.delete_environment(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
    )
    services.persist_workflow(
        execution_resource_name=execution_resource_name,
        project_id=data["project_id"],
        type=Workflow.DESTROY,
    )
    return JsonResponse({})


@require_GET
@login_required
@cloud_identity_required
@billing_setup_required
def is_workspace_setup_done(request):
    workspace_setup_finished = services.is_user_workspace_setup_done(user=request.user)
    return JsonResponse({"finished": workspace_setup_finished})


@require_GET
@login_required
@cloud_identity_required
@billing_setup_required
def check_execution_status(request):
    execution_resource_name = request.GET["execution_resource_name"]
    finished = services.check_if_execution_finished(
        execution_resource_name=execution_resource_name
    )
    if finished:
        services.mark_workflow_as_finished(
            execution_resource_name=execution_resource_name
        )
    return JsonResponse({"finished": finished})
