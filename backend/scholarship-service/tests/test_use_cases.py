import pytest

from app.application.use_cases import GetScholarship, ListScholarships
from app.domain.entities import Level, Scholarship
from app.domain.errors import ScholarshipNotFoundError
from app.domain.repositories import ScholarshipRepository

ITEM = Scholarship(
    id=7,
    name="Name",
    institution="Institution",
    level=Level.POSTGRADUATE,
    country="Perú",
    description="Desc",
)


class FakeScholarshipRepository(ScholarshipRepository):
    """Test double that implements the port (Liskov + Dependency Inversion)."""

    def __init__(self, items: list[Scholarship]):
        self._items = items

    def list_all(self) -> list[Scholarship]:
        return list(self._items)

    def get_by_id(self, scholarship_id: int) -> Scholarship | None:
        return next((item for item in self._items if item.id == scholarship_id), None)


def test_list_returns_repository_items():
    use_case = ListScholarships(FakeScholarshipRepository([ITEM]))
    assert use_case.execute() == [ITEM]


def test_get_returns_entity():
    use_case = GetScholarship(FakeScholarshipRepository([ITEM]))
    assert use_case.execute(7) == ITEM


def test_get_missing_raises_not_found():
    use_case = GetScholarship(FakeScholarshipRepository([]))
    with pytest.raises(ScholarshipNotFoundError):
        use_case.execute(999)
