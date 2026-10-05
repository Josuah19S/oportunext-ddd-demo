from app.domain.entities import Scholarship
from app.domain.errors import ScholarshipNotFoundError
from app.domain.repositories import ScholarshipRepository


class ListScholarships:
    def __init__(self, repository: ScholarshipRepository):
        self._repository = repository

    def execute(self) -> list[Scholarship]:
        return self._repository.list_all()


class GetScholarship:
    def __init__(self, repository: ScholarshipRepository):
        self._repository = repository

    def execute(self, scholarship_id: int) -> Scholarship:
        scholarship = self._repository.get_by_id(scholarship_id)
        if scholarship is None:
            raise ScholarshipNotFoundError(f"Scholarship {scholarship_id} not found")
        return scholarship
