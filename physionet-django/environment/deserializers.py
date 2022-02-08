from typing import List

from environment.entities import ResearchEnvironment


def deserialize_research_environments(data: dict) -> List[ResearchEnvironment]:
    return [
        ResearchEnvironment(
            id=workbench["id"],
            dataset=workbench["dataset"],
            region=workbench["region"],
            status=workbench["status"],
            type=workbench["type"],
        )
        for workspace in data["workspace-list"]
        for workbench in workspace["workbench-list"]
    ]
