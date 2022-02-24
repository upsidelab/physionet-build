from django.conf import settings

from project.models import AccessPolicy


def access_policy(request):
    return {'AccessPolicy': AccessPolicy}


def platform_config(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'FOOTER_MANAGED_BY': settings.FOOTER_MANAGED_BY,
        'FOOTER_SUPPORTED_BY': settings.FOOTER_SUPPORTED_BY,
        'FOOTER_ACCESSIBILITY_PAGE': settings.FOOTER_ACCESSIBILITY_PAGE,
        'STRAPLINE': settings.STRAPLINE,
    }


def enable_research_environments(request):
    return settings.ENABLE_RESEARCH_ENVIRONMENTS
