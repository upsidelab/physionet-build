import environment.api as api
from environment.models import CloudIdentity, BillingSetup
from environment.exceptions import IdentityProvisioningFailed, EnvironmentCreationFailed


def create_cloud_identity(user):
    response = api.create_cloud_identity(
        user.username, user.profile.first_names, user.profile.last_name
    )
    if not response.ok:
        raise IdentityProvisioningFailed()

    body = response.json()
    identity = CloudIdentity.objects.create(
        user=user, gcp_user_id=user.username, email=body["email-id"]
    )
    identity.otp = body["one-time-password"]
    return identity


def create_billing_setup(user, billing_account_id):
    cloud_identity = user.cloud_identity
    billing_setup = BillingSetup.objects.create(
        cloud_identity=cloud_identity, billing_account_id=billing_account_id
    )
    return billing_setup


def _create_workbench_kwargs(user, project, region, instance_type, environment_type):
    gcp_user_id = user.cloud_identity.gcp_user_id

    common = {
        "user_id": gcp_user_id,
        "region": region,
        "environment_type": environment_type,
        "instance_type": instance_type,
        "dataset": project.gcp.bucket_name,
    }
    if environment_type == "jupyter":
        jupyter_kwargs = {
            "vmimage": "common-cpu-notebooks",
            "persistentdisk": 10,                            # FIXME: Figure out what it should be
            "bucket_name": f"{gcp_user_id}-{project.slug}",  # FIXME: Figure out what it should be
        }
        return {**common, **jupyter_kwargs}
    else:
        return common


def create_research_environment(user, project, region, instance_type, environment_type):
    kwargs = _create_workbench_kwargs(
        user, project, region, instance_type, environment_type
    )
    response = api.create_workbench(**kwargs)
    if not response.ok:
        raise EnvironmentCreationFailed()

    return response
