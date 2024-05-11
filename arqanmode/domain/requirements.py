from dataclasses import dataclass
from enum import Enum


class RequirementSource(str, Enum):
    # Security Technical Implementation Guide
    STIG = 'stig'
    # International Electrotechnical Commission 62443 standard
    IEC_62443 = 'iec_62443'


class RequirementSeverity(str, Enum):
    UNKNOWN = 'unknown'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


@dataclass
class Requirement:
    title: str
    source: RequirementSource
    similar_requirements: list['Requirement']


@dataclass
class STIGRequirement(Requirement):
    id: str
    title: str
    description: str
    severity: RequirementSeverity
    platform: str
    url: str
    source = RequirementSource.STIG


@dataclass
class IEC62443Requirement(Requirement):
    title: str
    source = RequirementSource.IEC_62443


@dataclass
class Requirements:
    stig: list[STIGRequirement]
    iec_62443: list[IEC62443Requirement]
