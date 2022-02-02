def user_has_cloud_identity(user):
    return hasattr(user, "cloud_identity")


def user_has_billing_setup(user):
    if not user_has_cloud_identity(user):
        return False
    return hasattr(user.cloud_identity, "billing_setup")
