from pydantic import BaseModel

from app.domain.entities import Volunteering


class VolunteeringResponse(BaseModel):
    id: int
    title: str
    organization: str
    modality: str
    location: str
    description: str


def to_response(entity: Volunteering) -> VolunteeringResponse:
    return VolunteeringResponse(
        id=entity.id,
        title=entity.title,
        organization=entity.organization,
        modality=entity.modality.value,
        location=entity.location,
        description=entity.description,
    )
