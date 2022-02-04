from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

import environment.services as services
from environment.forms import BillingAccountIdForm, CreateResearchEnvironmentForm
from environment.decorators import cloud_identity_required, billing_setup_required
from environment.utilities import user_has_cloud_identity, user_has_billing_setup
from project.models import AccessPolicy, PublishedProject


@login_required
def identity_provisioning(request):
    if user_has_cloud_identity(request.user):
        return redirect("billing_setup")

    if request.method == "POST":
        identity = services.create_cloud_identity(request.user)
        request.session["cloud_identity_otp"] = identity.otp
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
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(
        access_policy=AccessPolicy.RESTRICTED
    )
    if request.user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    available_projects = PublishedProject.objects.filter(filters)

    return render(
        request,
        "environment/research_environments.html",
        {"available_projects": available_projects},
    )


@login_required
@cloud_identity_required
@billing_setup_required
def create_research_environment(request, project_slug):
    project = PublishedProject.objects.get(slug=project_slug)

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
