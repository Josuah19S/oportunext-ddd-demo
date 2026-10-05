from abc import ABC, abstractmethod

from .entities import Scholarship


class ScholarshipRepository(ABC):
    """Port: how the domain expects to access scholarship data."""

    @abstractmethod
    def list_all(self) -> list[Scholarship]: ...

    @abstractmethod
    def get_by_id(self, scholarship_id: int) -> Scholarship | None: ...
