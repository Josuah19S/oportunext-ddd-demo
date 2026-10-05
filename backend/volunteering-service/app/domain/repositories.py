from abc import ABC, abstractmethod

from .entities import Volunteering


class VolunteeringRepository(ABC):
    """Port: how the domain expects to access volunteering data."""

    @abstractmethod
    def list_all(self) -> list[Volunteering]: ...

    @abstractmethod
    def get_by_id(self, volunteering_id: int) -> Volunteering | None: ...
