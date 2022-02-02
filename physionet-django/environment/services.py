import environment.api as api
from environment.models import CloudIdentity, BillingSetup
from environment.exceptions import IdentityProvisioningFailed


def create_cloud_identity(user):
    response = api.create_cloud_identity(
        user.username, user.profile.first_names, user.profile.last_name
    )
    if not response.ok:
        raise IdentityProvisioningFailed()

    body = response.json()
    identity = CloudIdentity.objects.create(
        user=user, userid=user.username, email=body["email-id"]
    )
    identity.otp = body["one-time-password"]
    return identity


def create_billing_setup(user, billing_account_id):
    cloud_identity = user.cloud_identity
    billing_setup = BillingSetup.objects.create(
        cloud_identity=cloud_identity, billing_account_id=billing_account_id
    )
    return billing_setup
