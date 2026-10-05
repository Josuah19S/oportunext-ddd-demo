from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_returns_four_items():
    response = client.get("/volunteering")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_detail_returns_item():
    response = client.get("/volunteering/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Reforestación en Lurín",
        "organization": "Eco Perú",
        "modality": "in_person",
        "location": "Lima",
        "description": "Jornada de siembra de árboles nativos en la zona de lomas. Incluye una charla de capacitación al inicio.",
    }


def test_detail_missing_returns_404():
    response = client.get("/volunteering/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Volunteering 999 not found"}


def test_detail_non_integer_returns_422():
    assert client.get("/volunteering/abc").status_code == 422


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
