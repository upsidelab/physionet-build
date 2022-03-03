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
    require_DELETE,
    require_PATCH,
)
from environment.entities import Region, InstanceType
from environment.utilities import (
    user_has_cloud_identity,
    user_has_billing_setup,
)


@require_http_methods(["GET", "POST"])
@login_required
def identity_provisioning(request):
    # assuming that if user has could_identity => user has cloud_identity in API
    if user_has_cloud_identity(request.user):
        return redirect("billing_setup")

    # user has no cloud identity, and now we check if he has cloud identity in API
    user_info = services.get_user_info(request.user)
    if user_info.get('user-status') == 'user-added-in-cloud-identity':
        _identity = services.create_cloud_identity_object(
            user=request.user,
            gcp_user_id=user_info.get('user-id'),
            email=f'{user_info.get("user-id")}@healthdatanexus.ai'
            # FIXME replace hardcoded email when we get it in response
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
            # TODO: Billing setup has to be verified
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
    }
    return render(
        request,
        "environment/research_environments.html",
        context,
    )


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
            services.create_research_environment(
                user=request.user,
                project=project,
                region=form.cleaned_data["region"],
                instance_type=form.cleaned_data["instance_type"],
                environment_type=form.cleaned_data["environment_type"],
                persistent_disk=form.cleaned_data.get("persistent_disk"),
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
    services.stop_running_environment(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
    )
    return JsonResponse({})


@require_PATCH
@login_required
@cloud_identity_required
@billing_setup_required
def start_stopped_environment(request):
    data = json.loads(request.body)
    services.start_stopped_environment(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
    )
    return JsonResponse({})


@require_PATCH
@login_required
@cloud_identity_required
@billing_setup_required
def change_environment_instance_type(request):
    data = json.loads(request.body)
    services.change_environment_instance_type(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
        new_instance_type=InstanceType(data["instance_type"]),
    )
    return JsonResponse({})


@require_DELETE
@login_required
@cloud_identity_required
@billing_setup_required
def delete_environment(request):
    data = json.loads(request.body)
    services.delete_environment(
        user=request.user,
        workbench_id=data["workbench_id"],
        region=Region(data["region"]),
    )
    return JsonResponse({})
