from django.db.models import Q
from project.models import AccessPolicy, PublishedProject


def user_has_cloud_identity(user):
    return hasattr(user, "cloud_identity")


def user_has_billing_setup(user):
    if not user_has_cloud_identity(user):
        return False
    return hasattr(user.cloud_identity, "billing_setup")


def projects_available_for_user(user):
    filters = Q(access_policy=AccessPolicy.OPEN) | Q(
        access_policy=AccessPolicy.RESTRICTED
    )
    if user.is_credentialed:
        filters = filters | Q(access_policy=AccessPolicy.CREDENTIALED)

    return PublishedProject.objects.filter(filters)


def users_project_by_slug(user, project_slug):
    return projects_available_for_user(user).get(slug=project_slug)
