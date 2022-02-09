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
    DESTROYED = "destroyed"
    RUNNING = "running"


class EnvironmentType(Enum):
    JUPYTER = "jypyternotebook"  # Typo in API
    RSTUDIO = "rstudio"


@dataclass
class ResearchEnvironment:
    id: str
    dataset: str
    region: Region
    status: EnvironmentStatus
    type: EnvironmentType
    instance_type: InstanceType
