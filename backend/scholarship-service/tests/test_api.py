from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_returns_four_items():
    response = client.get("/scholarships")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_detail_returns_item():
    response = client.get("/scholarships/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Beca 18",
        "institution": "PRONABEC",
        "level": "undergraduate",
        "country": "Perú",
        "description": "Beca integral para estudios de pregrado dirigida a jóvenes con alto rendimiento y bajos recursos económicos.",
    }


def test_detail_missing_returns_404():
    response = client.get("/scholarships/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Scholarship 999 not found"}


def test_detail_non_integer_returns_422():
    assert client.get("/scholarships/abc").status_code == 422


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
