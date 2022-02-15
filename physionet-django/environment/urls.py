from django.urls import path

from environment import views


urlpatterns = [
    path("", views.research_environments, name="research_environments"),
    path(
        "identity-provisioning/",
        views.identity_provisioning,
        name="identity_provisioning",
    ),
    path("billing-setup/", views.billing_setup, name="billing_setup"),
    path(
        "environment/stop",
        views.stop_running_environment,
        name="stop_running_environment",
    ),
    path(
        "environment/start",
        views.start_stopped_environment,
        name="start_stopped_environment",
    ),
    path(
        "environment/update",
        views.change_environment_instance_type,
        name="change_environment_instance_type",
    ),
    path("environment/delete", views.delete_environment, name="delete_environment"),
    path(
        "create-research-environment/<project_slug>/",
        views.create_research_environment,
        name="create_research_environment",
    ),
]
