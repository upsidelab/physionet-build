import json
from typing import Optional

from django import template

from environment.entities import ResearchEnvironment, InstanceType


register = template.Library()


button_types = {
    "pause": {
        "http_method": "PATCH",
        "url_name": "stop_running_environment",
        "class": "btn btn-sm btn-primary m-1",
    },
    "start": {
        "http_method": "PATCH",
        "url_name": "start_stopped_environment",
        "class": "btn btn-sm btn-primary m-1",
    },
    "update": {
        "http_method": "PATCH",
        "url_name": "change_environment_instance_type",
        "class": "dropdown-item",
    },
    "destroy": {
        "http_method": "DELETE",
        "url_name": "delete_environment",
        "class": "btn btn-sm btn-danger m-1",
    },
}


@register.inclusion_tag("tag/environment_action_button.html")
def environment_action_button(
    environment: ResearchEnvironment,
    button_type: str,
    text: str,
    instance_type: Optional[str] = None,
) -> dict:
    button_type_data = button_types[button_type]
    request_data = {"workbench_id": environment.id, "region": environment.region.value}
    if instance_type:
        request_data["instance_type"] = instance_type

    return {
        "http_method": button_type_data["http_method"],
        "class": button_type_data["class"],
        "url_name": button_type_data["url_name"],
        "text": text,
        "request_data": json.dumps(request_data),
    }


@register.inclusion_tag("tag/environment_instance_change_dropdown.html")
def environment_instance_change_dropdown(environment: ResearchEnvironment) -> dict:
    instance_types = [t.value for t in InstanceType]
    return {
        "environment": environment,
        "instance_types": instance_types,
    }
