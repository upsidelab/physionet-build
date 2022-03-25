import json

from django import template
from django.urls import reverse
from django.db.models import Model

from environment.entities import ResearchEnvironment, InstanceType


PublishedProject = Model


register = template.Library()


button_types = {
    "pause": {
        "button_text": "Pause",
        "http_method": "PATCH",
        "url_name": "stop_running_environment",
        "button_class": "btn btn-primary m-1",
    },
    "start": {
        "button_text": "Start",
        "http_method": "PATCH",
        "url_name": "start_stopped_environment",
        "button_class": "btn btn-primary m-1",
    },
    "update": {
        "button_text": "Save Instance",
        "http_method": "PATCH",
        "url_name": "change_environment_instance_type",
        "button_class": "btn btn-primary",
    },
    "destroy": {
        "button_text": "Destroy",
        "http_method": "DELETE",
        "url_name": "delete_environment",
        "button_class": "btn btn-danger m-1",
    },
    "modal_instance": {
        "button_text": "Change Instance Type",
        "button_class": "btn-secondary",
        "modal_title": "Choose Instance Type",
        "modal_body": None,
        "action_button_type": "update",
    },
    "modal_pause": {
        "button_text": "Pause",
        "button_class": "btn-primary",
        "modal_title": "Pause",
        "modal_body": "Are you sure you want to pause this environment?",
        "action_button_type": "pause",
    },
    "modal_destroy": {
        "button_text": "Destroy",
        "button_class": "btn-danger",
        "modal_title": "Destroy",
        "modal_body": "Are you sure you want to destroy this environment?",
        "action_button_type": "destroy",
    },
    "modal_start": {
        "button_text": "Start",
        "button_class": "btn-primary",
        "modal_title": "Start",
        "modal_body": "Are you sure you want to start this environment?",
        "action_button_type": "start",
    },
}


@register.inclusion_tag("tag/environment_modal_button.html")
def environment_modal_button(
    environment: ResearchEnvironment,
    project: PublishedProject,
    button_type: str,
) -> dict:
    data = button_types[button_type]
    result_data = {
        "environment": environment,
        "project": project,
        "button_text": data["button_text"],
        "button_class": data["button_class"],
        "modal_title": data["modal_title"],
        "modal_body": data["modal_body"],
        "modal_id": f"{data['action_button_type']}-{environment.id}",
        "action_button_type": data["action_button_type"],
    }
    if button_type == "modal_instance":
        instance_types = [t.value for t in InstanceType]
        result_data["instance_types"] = instance_types

    return result_data


@register.inclusion_tag("tag/environment_action_button.html")
def environment_action_button(
    environment: ResearchEnvironment,
    project: PublishedProject,
    button_type: str,
) -> dict:
    data = button_types[button_type]
    request_data = {
        "workbench_id": environment.id,
        "project_id": project.pk,
        "region": environment.region.value,
    }

    result_data = {
        "button_class": data["button_class"],
        "button_text": data["button_text"],
        "button_type": button_type,
        "url": reverse(data["url_name"]),
        "http_method": data["http_method"],
        "request_data": json.dumps(request_data),
    }
    return result_data
