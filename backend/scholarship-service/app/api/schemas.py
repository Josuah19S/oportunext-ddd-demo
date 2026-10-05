from pydantic import BaseModel

from app.domain.entities import Scholarship


class ScholarshipResponse(BaseModel):
    id: int
    name: str
    institution: str
    level: str
    country: str
    description: str


def to_response(entity: Scholarship) -> ScholarshipResponse:
    return ScholarshipResponse(
        id=entity.id,
        name=entity.name,
        institution=entity.institution,
        level=entity.level.value,
        country=entity.country,
        description=entity.description,
    )
