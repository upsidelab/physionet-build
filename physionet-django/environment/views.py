from os import access
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from project.models import AccessPolicy, PublishedProject


@login_required
def research_environments(request):
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(access_policy=AccessPolicy.RESTRICTED)
    if request.user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    available_projects = PublishedProject.objects.filter(filters)

    return render(request, 'environment/research_environments.html', {'available_projects': available_projects})