from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_route_renders() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Deutsche Spielen" in response.text


def test_games_route_renders() -> None:
    response = client.get("/games")
    assert response.status_code == 200
    assert "Satzbauwuerfeln" in response.text


def test_satzbauwuerfeln_route_renders() -> None:
    response = client.get("/games/satzbauwuerfeln")
    assert response.status_code == 200
    assert "Klick auf" in response.text
