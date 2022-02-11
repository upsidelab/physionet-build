from typing import Optional
from dataclasses import dataclass
from enum import Enum


class EnumWithDefault(Enum):
    @classmethod
    def from_string_or_none(cls, maybe_string: Optional[str]) -> 'EnumWithDefault':
        if not maybe_string:
            return cls.UNKNOWN
        return cls(maybe_string)


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


class EnvironmentStatus(EnumWithDefault):
    UNKNOWN = "unknown"
    RUNNING = "running"
    DESTROYED = "destroyed"


class EnvironmentType(EnumWithDefault):
    UNKNOWN = "unknown"
    JUPYTER = "jypyternotebook" # Typo in API
    RSTUDIO = "rstudio"


@dataclass
class ResearchEnvironment:
    id: str
    dataset: str
    region: Region
    type: EnvironmentType
    instance_type: InstanceType
    status: EnvironmentStatus
    bucket_name: Optional[str]
    url: Optional[str]
