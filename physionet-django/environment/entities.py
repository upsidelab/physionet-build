from dataclasses import dataclass
from enum import Enum


class Region(Enum):
    US_CENTRAL = "us-central1"
    NORTHAMERICA_NORTHEAST = "northamerica_northeast1"
    EUROPE_WEST = "europe-west3"
    AUSTRALIA_SOUTHEAST = "australia-southeast1"


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
