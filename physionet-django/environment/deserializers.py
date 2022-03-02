from typing import Iterable

from environment.entities import (
    ResearchEnvironment,
    EnvironmentStatus,
    EnvironmentType,
    Region,
    InstanceType,
)


def deserialize_research_environments(data: dict) -> Iterable[ResearchEnvironment]:
    return [
        ResearchEnvironment(
            id=workbench["id"],
            dataset=workbench.get("dataset")
            or workbench.get("group-granting-data-access"),
            # FIXME Now we have to use both, dataset and group-granting-data-access in the future remove dataset
            url=workbench.get("url")
            or workbench.get("version-url"),  # RStudio sends version-url
            instance_type=InstanceType(workbench["machine-type"]),
            region=Region(workbench["region"]),
            bucket_name=workbench.get("bucket-name"),
            type=EnvironmentType.from_string_or_none(workbench["type"]),
            status=EnvironmentStatus(
                workbench["status"] or workbench["workbench-setup-status"]
            ),
        )
        for workspace in data["workspace-list"]
        for workbench in workspace["workbench-list"]
    ]
