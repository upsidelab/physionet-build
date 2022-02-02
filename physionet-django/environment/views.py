from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from environment.decorators import (
    cloud_identity_required,
    skip_if_cloud_identity_exists,
    billing_setup_required,
    skip_if_billing_setup_exists,
)
from environment.services import create_cloud_identity, create_billing_setup
from project.models import AccessPolicy, PublishedProject


@login_required
@skip_if_cloud_identity_exists
def identity_provisioning(request):
    if request.method == 'POST':
        identity = create_cloud_identity(request.user)
        request.session['cloud_identity_billing_data'] = {
            'otp': identity.otp,
            'billing_url': identity.billing_url
        }
        return redirect('billing_setup')
    return render(request, 'environment/identity_provisioning.html')


@login_required
@cloud_identity_required
@skip_if_billing_setup_exists
def billing_setup(request):
    if request.method == 'POST':
        # TODO: Billing setup has to be verified
        _billing_setup = create_billing_setup(request.user)
        return redirect('research_environments')
    context = request.session['cloud_identity_billing_data']
    return render(request, 'environment/billing_setup.html', context)


@login_required
@cloud_identity_required
@billing_setup_required
def research_environments(request):
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(access_policy=AccessPolicy.RESTRICTED)
    if request.user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    available_projects = PublishedProject.objects.filter(filters)

    return render(request, 'environment/research_environments.html', {'available_projects': available_projects})