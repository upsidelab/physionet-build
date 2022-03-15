from typing import Optional
from dataclasses import dataclass
from enum import Enum


class Region(Enum):
    US_CENTRAL = "us-central1"
    NORTHAMERICA_NORTHEAST = "northamerica-northeast1"
    EUROPE_WEST = "europe-west3"
    AUSTRALIA_SOUTHEAST = "australia-southeast1"


class InstanceType(Enum):
    N1_STANDARD_1 = "n1-standard-1"
    N1_STANDARD_2 = "n1-standard-2"
    N1_STANDARD_4 = "n1-standard-4"
    N1_STANDARD_8 = "n1-standard-8"
    N1_STANDARD_16 = "n1-standard-16"


class EnvironmentStatus(Enum):
    PROVISIONING = "inprogress"
    PROVISIONING_FAILED = "workbench-setup-failed"
    RUNNING = "running"
    UPDATING = "updating"
    TERMINATED = "terminated"  # Paused
    STOPPED = "stopped"
    DESTROYED = "destroyed"  # RStudio destroyed notebooks
    WORKBENCH_DESTROYED = "workbench-destroy-done"  # Jupyter destroyed notebooks
    # FIXME: Unify DESTROYED and WORKBENCH_DESTROYED


class EnvironmentType(Enum):
    UNKNOWN = "unknown"
    JUPYTER = "jypyternotebook"  # Typo in API
    RSTUDIO = "rstudio"

    @classmethod
    def from_string_or_none(cls, maybe_string: Optional[str]) -> "EnvironmentType":
        if not maybe_string:
            return cls.UNKNOWN
        return cls(maybe_string)


class WorkspaceStatus(Enum):
    DONE = "workspace-setup-done"
    INPROGRESS = "workspace-setup-inprogress"
    PENDING = "workspace-setup-pending"
    RETRYING = "workspace-setup-retrying"


@dataclass
class ResearchEnvironment:
    id: str
    group_granting_data_access: str
    region: Region
    type: EnvironmentType
    instance_type: InstanceType
    status: EnvironmentStatus
    bucket_name: Optional[str]
    url: Optional[str]

    @property
    def is_running(self):
        return self.status in [EnvironmentStatus.RUNNING, EnvironmentStatus.UPDATING]

    @property
    def is_paused(self):
        return self.status in [EnvironmentStatus.TERMINATED, EnvironmentStatus.STOPPED]

    @property
    def is_being_provisioned(self):
        return self.status == EnvironmentStatus.PROVISIONING

    @property
    def is_active(self):
        return self.is_running or self.is_paused or self.is_being_provisioned


@dataclass
class ResearchWorkspace:
    user_id: str
    region: Region
    gcp_project_id: str
    gcp_billing_id: str
    email_id: str
    workspace_setup_status: WorkspaceStatus

    @property
    def setup_finished(self):
        return self.workspace_setup_status == WorkspaceStatus.DONE
