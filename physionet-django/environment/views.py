from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from environment.services import ResearchEnvironmentService
from project.models import AccessPolicy, PublishedProject


@login_required
def research_environments(request):
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(access_policy=AccessPolicy.RESTRICTED)
    if request.user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    available_projects = PublishedProject.objects.filter(filters)

    return render(request, 'environment/research_environments.html', {'available_projects': available_projects})


@login_required
def set_up_billing_account(request):
    if request.method == "POST":
        # if billig account is not set up
        response = ResearchEnvironmentService.set_up_billing_account(user=request.user)

    return render(request, "")