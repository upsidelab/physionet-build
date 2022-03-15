from typing import Iterable, Optional

from environment.entities import (
    ResearchEnvironment,
    EnvironmentStatus,
    EnvironmentType,
    Region,
    InstanceType,
    ResearchWorkspace,
    WorkspaceStatus,
)


def _ensure_schema_in_url(
    url: Optional[str], schema: str = "https://"
) -> Optional[str]:
    if url is None or url.startswith(schema):
        return url
    return f"{schema}{url}"


def deserialize_research_environments(data: dict) -> Iterable[ResearchEnvironment]:
    return [
        ResearchEnvironment(
            id=workbench["id"],
            group_granting_data_access=workbench.get("group-granting-data-access"),
            url=_ensure_schema_in_url(
                workbench.get("url") or workbench.get("version-url")
            ),  # RStudio sends version-url
            instance_type=InstanceType(workbench["machine-type"]),
            region=Region(workbench["region"]),
            bucket_name=workbench.get("bucket-name"),
            type=EnvironmentType.from_string_or_none(workbench["type"]),
            status=EnvironmentStatus(workbench["workbench-setup-status"]),
        )
        for workspace in data["workspace-list"]
        for workbench in workspace["workbench-list"]
    ]


def deserialize_workspace_details(data: dict) -> ResearchWorkspace:
    return ResearchWorkspace(
        user_id=data["user-id"],
        region=data["region"],
        gcp_project_id=data["gcp-project-id"],
        gcp_billing_id=data["gcp-billing-id"],
        email_id=data["email-id"],
        workspace_setup_status=WorkspaceStatus(data["workspace-setup-status"]),
    )
