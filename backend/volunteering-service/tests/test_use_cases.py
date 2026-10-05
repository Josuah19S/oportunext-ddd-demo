import pytest

from app.application.use_cases import GetVolunteering, ListVolunteering
from app.domain.entities import Modality, Volunteering
from app.domain.errors import VolunteeringNotFoundError
from app.domain.repositories import VolunteeringRepository

ITEM = Volunteering(
    id=7,
    title="Title",
    organization="Org",
    modality=Modality.IN_PERSON,
    location="Lima",
    description="Desc",
)


class FakeVolunteeringRepository(VolunteeringRepository):
    """Test double that implements the port (Liskov + Dependency Inversion)."""

    def __init__(self, items: list[Volunteering]):
        self._items = items

    def list_all(self) -> list[Volunteering]:
        return list(self._items)

    def get_by_id(self, volunteering_id: int) -> Volunteering | None:
        return next((item for item in self._items if item.id == volunteering_id), None)


def test_list_returns_repository_items():
    use_case = ListVolunteering(FakeVolunteeringRepository([ITEM]))
    assert use_case.execute() == [ITEM]


def test_get_returns_entity():
    use_case = GetVolunteering(FakeVolunteeringRepository([ITEM]))
    assert use_case.execute(7) == ITEM


def test_get_missing_raises_not_found():
    use_case = GetVolunteering(FakeVolunteeringRepository([]))
    with pytest.raises(VolunteeringNotFoundError):
        use_case.execute(999)
