from app.domain.entities import Volunteering
from app.domain.errors import VolunteeringNotFoundError
from app.domain.repositories import VolunteeringRepository


class ListVolunteering:
    def __init__(self, repository: VolunteeringRepository):
        self._repository = repository

    def execute(self) -> list[Volunteering]:
        return self._repository.list_all()


class GetVolunteering:
    def __init__(self, repository: VolunteeringRepository):
        self._repository = repository

    def execute(self, volunteering_id: int) -> Volunteering:
        volunteering = self._repository.get_by_id(volunteering_id)
        if volunteering is None:
            raise VolunteeringNotFoundError(f"Volunteering {volunteering_id} not found")
        return volunteering
