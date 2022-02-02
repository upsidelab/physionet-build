import environment.api as api
from environment.models import CloudIdentity
from environment.exceptions import IdentityProvisioningFailed


def create_cloud_identity(user):
    response = api.create_cloud_identity(user.username, user.profile.first_names, user.profile.last_name)
    if not response.ok:
        raise IdentityProvisioningFailed()

    body = response.json()
    identity = CloudIdentity.objects.create(user=user, userid=user.username, email=body['email-id'])
    identity.otp = body['one-time-password']
    identity.billing_url = body['billingaccount-url']

    return identity