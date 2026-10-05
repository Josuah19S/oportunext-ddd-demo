import pytest

from app.domain.entities import Modality, Volunteering
from app.domain.errors import InvalidVolunteeringError

VALID = dict(
    id=1,
    title="Title",
    organization="Org",
    modality=Modality.REMOTE,
    location="Lima",
    description="Desc",
)


def test_valid_volunteering_is_created():
    volunteering = Volunteering(**VALID)
    assert volunteering.id == 1
    assert volunteering.modality is Modality.REMOTE


@pytest.mark.parametrize("bad_id", [0, -1])
def test_non_positive_id_is_rejected(bad_id):
    with pytest.raises(InvalidVolunteeringError):
        Volunteering(**{**VALID, "id": bad_id})


@pytest.mark.parametrize("field", ["title", "organization", "location"])
def test_empty_text_is_rejected(field):
    with pytest.raises(InvalidVolunteeringError):
        Volunteering(**{**VALID, field: "   "})


def test_invalid_modality_is_rejected():
    with pytest.raises(InvalidVolunteeringError):
        Volunteering(**{**VALID, "modality": "hybrid"})
