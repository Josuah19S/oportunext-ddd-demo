from app.domain.entities import Level, Scholarship
from app.domain.repositories import ScholarshipRepository

# Illustrative data: verify with official sources before using outside the demo.
SEED_DATA = [
    Scholarship(
        id=1,
        name="Beca 18",
        institution="PRONABEC",
        level=Level.UNDERGRADUATE,
        country="Perú",
        description="Beca integral para estudios de pregrado dirigida a jóvenes con alto rendimiento y bajos recursos económicos.",
    ),
    Scholarship(
        id=2,
        name="Beca Generación del Bicentenario",
        institution="PRONABEC",
        level=Level.POSTGRADUATE,
        country="Extranjero",
        description="Beca para estudios de posgrado en universidades del extranjero.",
    ),
    Scholarship(
        id=3,
        name="Chevening",
        institution="Gobierno del Reino Unido",
        level=Level.POSTGRADUATE,
        country="Reino Unido",
        description="Beca para estudios de maestría de un año en universidades del Reino Unido.",
    ),
    Scholarship(
        id=4,
        name="Fulbright",
        institution="Comisión Fulbright",
        level=Level.POSTGRADUATE,
        country="Estados Unidos",
        description="Beca para estudios de posgrado en universidades de Estados Unidos.",
    ),
]


class InMemoryScholarshipRepository(ScholarshipRepository):
    """Adapter: keeps scholarships in memory, loaded with seed data."""

    def __init__(self) -> None:
        self._items: dict[int, Scholarship] = {item.id: item for item in SEED_DATA}

    def list_all(self) -> list[Scholarship]:
        return sorted(self._items.values(), key=lambda item: item.id)

    def get_by_id(self, scholarship_id: int) -> Scholarship | None:
        return self._items.get(scholarship_id)
