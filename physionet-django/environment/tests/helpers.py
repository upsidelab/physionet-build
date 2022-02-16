from django.contrib.auth import get_user_model

from environment.models import CloudIdentity, BillingSetup

User = get_user_model()


def create_user_without_cloud_identity() -> User:
    return User.objects.create_user("foo", "bar", "baz")


def create_user_with_cloud_identity() -> User:
    user = create_user_without_cloud_identity()
    CloudIdentity.objects.create(
        user=user,
        gcp_user_id=user.username,
        email=user.email,
    )
    return user


def create_user_with_billing_setup() -> User:
    user = create_user_with_cloud_identity()
    BillingSetup.objects.create(
        cloud_identity=user.cloud_identity, billing_account_id="XXXXXX-XXXXXX-XXXXXX"
    )
    return user
