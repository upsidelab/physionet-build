from user.models import User


def user_has_cloud_identity(user: User) -> bool:
    return hasattr(user, "cloud_identity")


def user_has_billing_setup(user: User) -> bool:
    if not user_has_cloud_identity(user):
        return False
    return hasattr(user.cloud_identity, "billing_setup")
