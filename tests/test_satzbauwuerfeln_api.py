from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_roll_returns_200():
    response = client.post("/api/games/satzbauwuerfeln/roll")
    assert response.status_code == 200


def test_roll_response_schema():
    data = client.post("/api/games/satzbauwuerfeln/roll").json()
    assert "dice" in data
    assert "sentence_type" in data
    assert len(data["dice"]) == 3
    for die in data["dice"]:
        assert "value" in die
        assert "label" in die
        assert "question" in die
        assert "suggestion" in die
    assert data["sentence_type"]["letter"] in "ABCDEF"
    assert data["sentence_type"]["label"]


def test_roll_dice_values_are_unique():
    data = client.post("/api/games/satzbauwuerfeln/roll").json()
    values = [d["value"] for d in data["dice"]]
    assert len(set(values)) == 3


def test_roll_dice_values_in_range():
    data = client.post("/api/games/satzbauwuerfeln/roll").json()
    for die in data["dice"]:
        assert 1 <= die["value"] <= 6


# --- /validate ---

def _validate(sentence, suggestions, letter):
    return client.post(
        "/api/games/satzbauwuerfeln/validate",
        json={"sentence": sentence, "suggestions": suggestions, "sentence_type_letter": letter},
    )


def test_validate_returns_200():
    res = _validate("Mein Bruder spielt Fußball.", ["spielen", "Bruder", "Fußball"], "F")
    assert res.status_code == 200


def test_validate_response_schema():
    data = _validate("Mein Bruder spielt Fußball.", ["spielen", "Bruder", "Fußball"], "F").json()
    assert "is_valid" in data
    assert "checks_passed" in data
    assert "checks_failed" in data
    assert "message" in data


def test_validate_valid_sentence():
    data = _validate("Mein Bruder spielt Fußball.", ["spielen", "Bruder", "Fußball"], "F").json()
    assert data["is_valid"] is True
    assert data["checks_failed"] == []


def test_validate_empty_sentence():
    data = _validate("", ["spielen", "Bruder", "Fußball"], "A").json()
    assert data["is_valid"] is False
    assert "non_empty" in data["checks_failed"]


def test_validate_invalid_letter_returns_422():
    res = client.post(
        "/api/games/satzbauwuerfeln/validate",
        json={"sentence": "Test.", "suggestions": [], "sentence_type_letter": "Z"},
    )
    assert res.status_code == 422
