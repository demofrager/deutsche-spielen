import re
from dataclasses import dataclass, field

from app.services.grammar_service import check_grammar

# Articles / prepositions to ignore when matching suggestion tokens
_STOP_WORDS = {
    "der", "die", "das", "dem", "den", "des",
    "ein", "eine", "einen", "einem", "einer", "eines",
    "am", "im", "in", "an", "auf", "zu", "um", "bei",
    "von", "aus", "mit", "nach", "vor", "seit",
}

_SUBORD_CONJUNCTIONS = {
    "weil", "dass", "obwohl", "wenn", "als", "damit",
    "nachdem", "bevor", "bis", "während", "falls",
    "sofern", "seitdem", "sodass",
}

_HABEN_SEIN = {
    "habe", "hast", "hat", "haben", "habt",
    "hatte", "hattest", "hatten", "hattet",
    "bin", "bist", "ist", "sind", "seid",
    "war", "warst", "waren", "wart",
}

_WERDEN = {"werde", "wirst", "wird", "werden", "werdet"}

_POSSESSIVE_STEMS = {"mein", "dein", "sein", "ihr", "unser", "euer"}

_FINITE_VERB_FORMS = {
    # sein
    "bin", "bist", "ist", "sind", "seid", "war", "warst", "waren", "wart",
    # haben
    "habe", "hast", "hat", "haben", "habt", "hatte", "hattest", "hattet",
    # werden
    "werde", "wirst", "wird", "werden", "werdet", "wurde", "wurden",
    # modal verbs (common finite forms)
    "kann", "kannst", "können", "könnt",
    "muss", "musst", "müssen", "müsst",
    "will", "willst", "wollen", "wollt",
    "soll", "sollst", "sollen", "sollt",
    "darf", "darfst", "dürfen", "dürft",
    "mag", "magst", "mögen", "mögt",
}

_SUBJECT_PRONOUNS = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich", "uns", "euch",
}


@dataclass
class ValidationResult:
    is_valid: bool
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    message: str = ""
    grammar_errors: list[str] = field(default_factory=list)
    grammar_replacements: list[list[str]] = field(default_factory=list)


def _content_words(phrase: str) -> list[str]:
    """Return lower-case non-stop words from a suggestion phrase."""
    words: list[str] = []
    for raw in phrase.lower().split():
        normalized = re.sub(r"[^\w]", "", raw)
        if normalized and normalized not in _STOP_WORDS:
            words.append(normalized)
    return words


def _tokenize_sentence(sentence: str) -> list[str]:
    return re.findall(r"\w+", sentence.lower())


def _word_matches(sentence_words: list[str], suggestion_word: str) -> bool:
    for sentence_word in sentence_words:
        if sentence_word == suggestion_word:
            return True

        # Lightweight morphology tolerance (e.g. spielen <-> spielt)
        min_len = min(len(sentence_word), len(suggestion_word))
        if min_len >= 4 and sentence_word[:4] == suggestion_word[:4]:
            return True

    return False


def validate_sentence(
    sentence: str,
    suggestions: list[str],
    sentence_type_letter: str,
    required_suggestion_matches: int = 2,
) -> ValidationResult:
    checks_passed: list[str] = []
    checks_failed: list[str] = []

    # 1. Non-empty
    stripped = sentence.strip()
    if not stripped:
        return ValidationResult(
            is_valid=False,
            checks_passed=[],
            checks_failed=["non_empty"],
            message="Dein Satz ist leer. Bitte schreib einen Satz.",
            grammar_errors=[],
        )
    checks_passed.append("non_empty")

    # 2. Ends with valid punctuation
    if stripped[-1] in ".?!":
        checks_passed.append("punctuation")
    else:
        checks_failed.append("punctuation")

    # 3. Contains at least `required_suggestion_matches` suggestion tokens
    sentence_lower = stripped.lower()
    sentence_words = _tokenize_sentence(stripped)
    matches = sum(
        1 for s in suggestions
        if any(_word_matches(sentence_words, w) for w in _content_words(s))
    )
    if matches >= required_suggestion_matches:
        checks_passed.append("contains_suggestions")
    else:
        checks_failed.append("contains_suggestions")

    # 4. Sentence-type heuristic
    if _sentence_type_heuristic(stripped, sentence_lower, sentence_type_letter):
        checks_passed.append("sentence_type_hint")
    else:
        checks_failed.append("sentence_type_hint")

    # 5. Lightweight German structure checks (word order / finite verb)
    if _word_order_heuristic(stripped, sentence_lower, sentence_type_letter):
        checks_passed.append("word_order_hint")
    else:
        checks_failed.append("word_order_hint")

    # 6. Grammar checks for hints (LanguageTool) — skip if blocking failures already found
    if checks_failed:
        grammar_issues = []
    else:
        grammar_issues = check_grammar(stripped)
    grammar_errors = [issue.message for issue in grammar_issues]
    grammar_replacements = [issue.replacements for issue in grammar_issues]
    if grammar_errors:
        checks_failed.append("grammar_errors")
    else:
        checks_passed.append("grammar_errors")

    blocking_failures = [c for c in checks_failed if c != "grammar_errors"]
    is_valid = len(blocking_failures) == 0
    return ValidationResult(
        is_valid=is_valid,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        message=_build_message(is_valid, checks_failed, sentence_type_letter, grammar_errors, grammar_replacements),
        grammar_errors=grammar_errors,
        grammar_replacements=grammar_replacements,
    )


def _sentence_type_heuristic(sentence: str, sentence_lower: str, letter: str) -> bool:
    words = sentence_lower.split()
    first = words[0] if words else ""
    stripped = sentence.strip()
    is_question_punctuation = stripped.endswith("?")

    # Question punctuation should only be used for question sentence type (C).
    if letter != "C" and is_question_punctuation:
        return False

    if letter == "A":   # Hauptsatz: must NOT start with subordinating conjunction
        return first not in _SUBORD_CONJUNCTIONS
    if letter == "B":   # Nebensatz: must contain a subordinating conjunction
        return any(c in words for c in _SUBORD_CONJUNCTIONS)
    if letter == "C":   # Fragesatz: must end with ?
        return is_question_punctuation
    if letter == "D":   # Infinitiv + zu: must contain " zu "
        return " zu " in sentence_lower
    if letter == "E":   # Perfekt / Futur: auxiliary verb
        return bool((_HABEN_SEIN | _WERDEN) & set(words))
    if letter == "F":   # Possessivartikel
        return any(re.search(r"\b" + stem, sentence_lower) for stem in _POSSESSIVE_STEMS)
    return True


def _is_likely_finite_verb(word: str) -> bool:
    if not word:
        return False
    if word in _FINITE_VERB_FORMS:
        return True
    # "gegessen", "gemacht" etc. are usually participles, not finite verbs.
    if word.startswith("ge") and word.endswith("en"):
        return False
    # Very lightweight finite endings for present/past singular forms.
    return len(word) >= 3 and (word.endswith("e") or word.endswith("st") or word.endswith("t"))


def _first_finite_verb_index(words: list[str]) -> int | None:
    for i, w in enumerate(words):
        if _is_likely_finite_verb(w):
            return i
    return None


def _word_order_heuristic(sentence: str, sentence_lower: str, letter: str) -> bool:
    words = _tokenize_sentence(sentence)
    if len(words) < 2:
        return True

    finite_idx = _first_finite_verb_index(words)

    # Most sentence types should contain at least one finite verb.
    if letter in {"A", "C", "D", "E", "F"} and finite_idx is None:
        return False

    # Hauptsatz-like patterns: finite verb should appear early (V2-ish).
    if letter in {"A", "D", "E", "F"}:
        return finite_idx is not None and finite_idx <= 3

    # Fragesatz: often verb-first or question word + verb.
    if letter == "C":
        return finite_idx is not None and finite_idx <= 2

    # Nebensatz: if a conjunction exists, finite verb should be near the end.
    if letter == "B":
        has_subord = any(c in words for c in _SUBORD_CONJUNCTIONS)
        if not has_subord:
            return True
        if finite_idx is None:
            return False
        return finite_idx >= max(0, len(words) - 2)

    return True


def _build_message(
    is_valid: bool,
    checks_failed: list[str],
    letter: str,
    grammar_errors: list[str],
    grammar_replacements: list[list[str]] | None = None,
) -> str:
    grammar_replacements = grammar_replacements or []

    def grammar_hint(index: int = 0) -> str:
        hint = grammar_errors[index]
        repls = grammar_replacements[index] if index < len(grammar_replacements) else []
        if repls:
            hint += f" (Vorschlag: {repls[0]})"
        return hint

    if is_valid:
        if grammar_errors:
            return (
                "Dein Satz erfüllt die Aufgabenregeln, aber es gibt Grammatik-Hinweise: "
                + grammar_hint()
            )
        return "Sehr gut! Dein Satz sieht richtig aus. \U0001f389"
    hints: list[str] = []
    if "punctuation" in checks_failed:
        hints.append("Vergiss das Satzzeichen am Ende nicht (. ? !).")
    if "contains_suggestions" in checks_failed:
        hints.append("Versuche, mindestens zwei der gewürfelten Wörter zu verwenden.")
    if "sentence_type_hint" in checks_failed:
        hints.append(_sentence_type_hint(letter))
    if "word_order_hint" in checks_failed:
        hints.append("Achte auf die deutsche Satzstellung: Das finite Verb muss an der richtigen Position stehen.")
    if grammar_errors:
        hints.append(f"Grammatik-Hinweis: {grammar_hint()}")
    return " ".join(hints) if hints else "Überprüfe deinen Satz noch einmal."


def _sentence_type_hint(letter: str) -> str:
    return {
        "A": "Ein Hauptsatz beginnt nicht mit einer unterordnenden Konjunktion.",
        "B": "Ein Nebensatz braucht eine unterordnende Konjunktion (z.B. weil, dass, wenn).",
        "C": "Ein Fragesatz endet mit einem Fragezeichen (?).",
        "D": "Vergiss nicht das 'zu' vor dem Infinitiv.",
        "E": "Verwende ein Hilfsverb (haben, sein, werden) für Perfekt oder Futur.",
        "F": "Verwende einen Possessivartikel (mein, dein, sein, ihr, unser, euer).",
    }.get(letter, "Überprüfe den Satztyp.")
