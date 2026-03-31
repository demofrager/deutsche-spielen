import httpx

from app.services import grammar_service


def test_check_grammar_returns_empty_when_not_configured(monkeypatch):
    monkeypatch.delenv("LANGUAGETOOL_URL", raising=False)
    issues = grammar_service.check_grammar("Das ist ein Test.")
    assert issues == []


def test_check_grammar_parses_matches(monkeypatch):
    monkeypatch.setenv("LANGUAGETOOL_URL", "http://localhost:8081")

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "matches": [
                    {
                        "message": "Möglicher Tippfehler gefunden.",
                        "offset": 8,
                        "length": 4,
                        "replacements": [{"value": "Test"}, {"value": "fest"}],
                        "rule": {"id": "GERMAN_SPELLER_RULE"},
                    }
                ]
            }

    def fake_post(*args, **kwargs):
        # Verify correct request parameters are sent
        assert kwargs["data"]["language"] == "de-DE"
        assert kwargs["data"]["enabledOnly"] == "false"
        assert kwargs["headers"]["Accept"] == "application/json"
        return DummyResponse()

    monkeypatch.setattr(grammar_service.httpx, "post", fake_post)
    issues = grammar_service.check_grammar("Das ist test.")

    assert len(issues) == 1
    assert issues[0].message == "Möglicher Tippfehler gefunden."
    assert issues[0].rule_id == "GERMAN_SPELLER_RULE"
    assert issues[0].replacements == ["Test", "fest"]


def test_check_grammar_returns_empty_on_http_error(monkeypatch):
    monkeypatch.setenv("LANGUAGETOOL_URL", "http://localhost:8081")

    def fake_post(*args, **kwargs):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(grammar_service.httpx, "post", fake_post)
    issues = grammar_service.check_grammar("Das ist ein Test.")
    assert issues == []