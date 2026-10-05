from dataclasses import dataclass
from enum import Enum

from .errors import InvalidVolunteeringError


class Modality(str, Enum):
    IN_PERSON = "in_person"
    REMOTE = "remote"


@dataclass(frozen=True)
class Volunteering:
    id: int
    title: str
    organization: str
    modality: Modality
    location: str
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, int) or self.id <= 0:
            raise InvalidVolunteeringError("id must be a positive integer")
        for field_name in ("title", "organization", "location"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidVolunteeringError(f"{field_name} must not be empty")
        if not isinstance(self.modality, Modality):
            raise InvalidVolunteeringError("modality must be a Modality")
