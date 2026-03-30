import re
from dataclasses import dataclass, field

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


@dataclass
class ValidationResult:
    is_valid: bool
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    message: str = ""


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

    is_valid = len(checks_failed) == 0
    return ValidationResult(
        is_valid=is_valid,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        message=_build_message(is_valid, checks_failed, sentence_type_letter),
    )


def _sentence_type_heuristic(sentence: str, sentence_lower: str, letter: str) -> bool:
    words = sentence_lower.split()
    first = words[0] if words else ""

    if letter == "A":   # Hauptsatz: must NOT start with subordinating conjunction
        return first not in _SUBORD_CONJUNCTIONS
    if letter == "B":   # Nebensatz: must contain a subordinating conjunction
        return any(c in words for c in _SUBORD_CONJUNCTIONS)
    if letter == "C":   # Fragesatz: must end with ?
        return sentence.strip().endswith("?")
    if letter == "D":   # Infinitiv + zu: must contain " zu "
        return " zu " in sentence_lower
    if letter == "E":   # Perfekt / Futur: auxiliary verb
        return bool((_HABEN_SEIN | _WERDEN) & set(words))
    if letter == "F":   # Possessivartikel
        return any(re.search(r"\b" + stem, sentence_lower) for stem in _POSSESSIVE_STEMS)
    return True


def _build_message(is_valid: bool, checks_failed: list[str], letter: str) -> str:
    if is_valid:
        return "Sehr gut! Dein Satz sieht richtig aus. \U0001f389"
    hints: list[str] = []
    if "punctuation" in checks_failed:
        hints.append("Vergiss das Satzzeichen am Ende nicht (. ? !).")
    if "contains_suggestions" in checks_failed:
        hints.append("Versuche, mindestens zwei der gewürfelten Wörter zu verwenden.")
    if "sentence_type_hint" in checks_failed:
        hints.append(_sentence_type_hint(letter))
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
