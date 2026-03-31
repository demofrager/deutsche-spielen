import os
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class GrammarIssue:
    message: str
    rule_id: str
    offset: int
    length: int
    replacements: list[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "replacements", self.replacements or [])


def get_languagetool_url() -> str | None:
    """Return configured LanguageTool base URL, if enabled."""
    raw = os.getenv("LANGUAGETOOL_URL", "").strip()
    return raw.rstrip("/") if raw else None


def is_languagetool_available(timeout_seconds: float = 1.5) -> bool:
    """Best-effort availability check for LanguageTool."""
    base_url = get_languagetool_url()
    if not base_url:
        return False

    try:
        response = httpx.get(f"{base_url}/v2/languages", timeout=timeout_seconds)
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False


def check_grammar(
    sentence: str,
    language: str = "de-DE",
    timeout_seconds: float = 3.0,
) -> list[GrammarIssue]:
    """Return grammar issues from LanguageTool.

    If the service is not configured or unavailable, return an empty list.
    """
    base_url = get_languagetool_url()
    if not base_url:
        return []

    try:
        response = httpx.post(
            f"{base_url}/v2/check",
            data={"text": sentence, "language": language, "enabledOnly": "false"},
            headers={"Accept": "application/json"},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        matches = payload.get("matches", [])
        issues: list[GrammarIssue] = []
        for match in matches:
            rule = match.get("rule", {})
            replacements = [r["value"] for r in match.get("replacements", []) if "value" in r]
            issues.append(
                GrammarIssue(
                    message=match.get("message", "Grammar issue detected."),
                    rule_id=rule.get("id", "UNKNOWN_RULE"),
                    offset=int(match.get("offset", 0)),
                    length=int(match.get("length", 0)),
                    replacements=replacements,
                )
            )
        return issues
    except (httpx.HTTPError, ValueError, TypeError):
        return []