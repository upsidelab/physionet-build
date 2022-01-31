from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from project.models import AccessPolicy, PublishedProject
from environment.api import create_cloud_identity


@login_required
def identity_provisioning(request):
    if request.method == 'POST':
        user = request.user
        response = create_cloud_identity(user.username, user.profile.first_names, user.profile.last_name)
        if response.ok:
            body = response.json()
            # Session is a bad idea - store in DB
            request.session['research_environment_data'] = {
                'billing_url': body['billingaccount-url'],
                'email': body['email-id'],
                'otp': body['one-time-password'],
            }
            return redirect('billing_setup')
        else:
            raise Exception('Identity Provisioning failed.')

    return render(request, 'environment/identity_provisioning.html')


@login_required
def billing_setup(request):
    if not request.session['research_environment_data']:
        return redirect(request, 'identity_provisioning')
    
    context = request.session['research_environment_data']
    return render(request, 'environment/billing_setup.html', context)


@login_required
def research_environments(request):
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(access_policy=AccessPolicy.RESTRICTED)
    if request.user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    available_projects = PublishedProject.objects.filter(filters)

    return render(request, 'environment/research_environments.html', {'available_projects': available_projects})