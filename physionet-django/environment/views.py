from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

import environment.services as services
from environment.forms import BillingAccountIdForm, CreateResearchEnvironmentForm
from environment.decorators import cloud_identity_required, billing_setup_required
from environment.utilities import user_has_cloud_identity, user_has_billing_setup, users_project_by_slug


@login_required
def identity_provisioning(request):
    if user_has_cloud_identity(request.user):
        return redirect("billing_setup")

    if request.method == "POST":
        otp, _ = services.create_cloud_identity(request.user)
        request.session["cloud_identity_otp"] = otp
        return redirect("billing_setup")

    return render(request, "environment/identity_provisioning.html")


@login_required
@cloud_identity_required
def billing_setup(request):
    if user_has_billing_setup(request.user):
        return redirect("research_environments")

    if request.method == "POST":
        form = BillingAccountIdForm(request.POST)
        if form.is_valid():
            # TODO: Billing setup has to be verified
            services.create_billing_setup(
                request.user, form.cleaned_data["billing_account_id"]
            )
            return redirect("research_environments")
    else:
        form = BillingAccountIdForm()

    cloud_identity = request.user.cloud_identity
    context = {
        "email": cloud_identity.email,
        "otp": request.session.get("cloud_identity_otp"),
        "form": form,
    }
    return render(request, "environment/billing_setup.html", context)


@login_required
@cloud_identity_required
@billing_setup_required
def research_environments(request):
    available_projects = services.get_available_projects(request.user)
    available_environments = services.get_available_environments(request.user)
    project_environment_pairs = services.match_projects_with_environments(
        available_projects, available_environments
    )
    environment_project_pairs = [
        (environment, project)
        for (project, environment) in project_environment_pairs
        if environment is not None
    ]
    context = {
        "project_environment_pairs": project_environment_pairs,
        "environment_project_pairs": environment_project_pairs,
    }
    return render(
        request,
        "environment/research_environments.html",
        context,
    )


@login_required
@cloud_identity_required
@billing_setup_required
def create_research_environment(request, project_slug):
    project = users_project_by_slug(request.user, project_slug)

    if request.method == "POST":
        form = CreateResearchEnvironmentForm(request.POST)
        if form.is_valid():
            services.create_research_environment(
                user=request.user,
                project=project,
                region=form.cleaned_data["region"],
                instance_type=form.cleaned_data["instance_type"],
                environment_type=form.cleaned_data["environment_type"],
            )
            return redirect("research_environments")
    else:
        form = CreateResearchEnvironmentForm()

    context = {"form": form, "project": project}
    return render(request, "environment/create_research_environment.html", context)
