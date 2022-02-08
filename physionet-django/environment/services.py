from typing import Tuple, Iterable

from django.db.models import Q

import environment.api as api
from environment.models import CloudIdentity, BillingSetup
from environment.exceptions import IdentityProvisioningFailed
from environment.deserializers import deserialize_research_environments
from environment.entities import ResearchEnvironment
from user.models import User
from project.models import AccessPolicy, PublishedProject


def create_cloud_identity(user: User) -> Tuple[str, CloudIdentity]:
    response = api.create_cloud_identity(
        user.username, user.profile.first_names, user.profile.last_name
    )
    if not response.ok:
        raise IdentityProvisioningFailed()

    body = response.json()
    identity = CloudIdentity.objects.create(
        user=user, gcp_user_id=user.username, email=body["email-id"]
    )
    otp = body["one-time-password"]
    return otp, identity


def create_billing_setup(user: User, billing_account_id: str) -> BillingSetup:
    cloud_identity = user.cloud_identity
    billing_setup = BillingSetup.objects.create(
        cloud_identity=cloud_identity, billing_account_id=billing_account_id
    )
    return billing_setup


def get_available_projects(user: User) -> Iterable[PublishedProject]:
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(
        access_policy=AccessPolicy.RESTRICTED
    )
    if user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    return PublishedProject.objects.filter(filters)


def get_all_environments(user: User) -> Iterable[ResearchEnvironment]:
    gcp_user_id = user.cloud_identity.gcp_user_id
    response = api.get_workspace_list(gcp_user_id)
    environments = deserialize_research_environments(response.json())

    return environments
