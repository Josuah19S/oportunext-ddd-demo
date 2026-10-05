import pytest

from app.domain.entities import Level, Scholarship
from app.domain.errors import InvalidScholarshipError

VALID = dict(
    id=1,
    name="Name",
    institution="Institution",
    level=Level.UNDERGRADUATE,
    country="Perú",
    description="Desc",
)


def test_valid_scholarship_is_created():
    scholarship = Scholarship(**VALID)
    assert scholarship.id == 1
    assert scholarship.level is Level.UNDERGRADUATE


@pytest.mark.parametrize("bad_id", [0, -1])
def test_non_positive_id_is_rejected(bad_id):
    with pytest.raises(InvalidScholarshipError):
        Scholarship(**{**VALID, "id": bad_id})


@pytest.mark.parametrize("field", ["name", "institution", "country"])
def test_empty_text_is_rejected(field):
    with pytest.raises(InvalidScholarshipError):
        Scholarship(**{**VALID, field: "   "})


def test_invalid_level_is_rejected():
    with pytest.raises(InvalidScholarshipError):
        Scholarship(**{**VALID, "level": "doctorate"})
