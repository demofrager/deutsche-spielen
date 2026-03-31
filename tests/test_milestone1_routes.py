from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_route_renders() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Deutsche Spielen" in response.text
    assert 'href="/games"' in response.text
    assert "Wortschatzblitz (Stub)" not in response.text


def test_games_route_renders() -> None:
    response = client.get("/games")
    assert response.status_code == 200
    assert "Satzbauwuerfeln" in response.text
    assert 'href="/games/satzbauwuerfeln"' in response.text
    assert "/games/wortschatzblitz" not in response.text


def test_satzbauwuerfeln_route_renders() -> None:
    response = client.get("/games/satzbauwuerfeln")
    assert response.status_code == 200
    assert "Klick auf" in response.text


def test_hidden_stub_route_is_accessible_directly() -> None:
    response = client.get("/games/wortschatzblitz")
    assert response.status_code == 200
    assert "Wortschatzblitz (Stub)" in response.text
