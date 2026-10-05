from app.domain.entities import Modality, Volunteering
from app.domain.repositories import VolunteeringRepository

SEED_DATA = [
    Volunteering(
        id=1,
        title="Reforestación en Lurín",
        organization="Eco Perú",
        modality=Modality.IN_PERSON,
        location="Lima",
        description="Jornada de siembra de árboles nativos en la zona de lomas. Incluye una charla de capacitación al inicio.",
    ),
    Volunteering(
        id=2,
        title="Mentoría escolar en línea",
        organization="Educa Más",
        modality=Modality.REMOTE,
        location="Remoto",
        description="Acompañamiento semanal a estudiantes de secundaria en matemática y comprensión lectora.",
    ),
    Volunteering(
        id=3,
        title="Apoyo en comedor popular",
        organization="Manos Unidas",
        modality=Modality.IN_PERSON,
        location="Cusco",
        description="Preparación y reparto de raciones en un comedor popular del distrito.",
    ),
    Volunteering(
        id=4,
        title="Limpieza de playas",
        organization="Mar Limpio",
        modality=Modality.IN_PERSON,
        location="Lima",
        description="Campaña de recolección de residuos y educación ambiental para vecinos.",
    ),
]


class InMemoryVolunteeringRepository(VolunteeringRepository):
    """Adapter: keeps volunteering in memory, loaded with seed data."""

    def __init__(self) -> None:
        self._items: dict[int, Volunteering] = {item.id: item for item in SEED_DATA}

    def list_all(self) -> list[Volunteering]:
        return sorted(self._items.values(), key=lambda item: item.id)

    def get_by_id(self, volunteering_id: int) -> Volunteering | None:
        return self._items.get(volunteering_id)
