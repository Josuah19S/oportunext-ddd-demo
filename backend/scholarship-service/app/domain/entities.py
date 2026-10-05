from dataclasses import dataclass
from enum import Enum

from .errors import InvalidScholarshipError


class Level(str, Enum):
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"


@dataclass(frozen=True)
class Scholarship:
    id: int
    name: str
    institution: str
    level: Level
    country: str
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, int) or self.id <= 0:
            raise InvalidScholarshipError("id must be a positive integer")
        for field_name in ("name", "institution", "country"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidScholarshipError(f"{field_name} must not be empty")
        if not isinstance(self.level, Level):
            raise InvalidScholarshipError("level must be a Level")
