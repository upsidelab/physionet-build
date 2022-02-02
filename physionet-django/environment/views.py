from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from environment.forms import BillingAccountIdForm
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
        request.session['cloud_identity_otp'] = identity.otp
        return redirect('billing_setup')
    return render(request, 'environment/identity_provisioning.html')


@login_required
@cloud_identity_required
@skip_if_billing_setup_exists
def billing_setup(request):
    if request.method == 'POST':
        form = BillingAccountIdForm(request.POST)
        if form.is_valid():
            # TODO: Billing setup has to be verified
            create_billing_setup(request.user, form.cleaned_data['billing_account_id'])
            return redirect('research_environments')
    else:
        form = BillingAccountIdForm()

    cloud_identity = request.user.cloud_identity
    context = {
        'email': cloud_identity.email,
        'otp': request.session.get('cloud_identity_otp'),
        'form': form,
    }
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