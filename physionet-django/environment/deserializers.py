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
            dataset=workbench["dataset"],
            region=Region(workbench["region"]),
            status=EnvironmentStatus(workbench["status"]),
            type=EnvironmentType(workbench["type"]),
            instance_type=InstanceType(workbench["machine-type"]),
            bucket_name=workbench.get("bucket-name"), # FIXME: Optional here for now - has to be set for Jupyter notebooks
        )
        for workspace in data["workspace-list"]
        for workbench in workspace["workbench-list"]
    ]
