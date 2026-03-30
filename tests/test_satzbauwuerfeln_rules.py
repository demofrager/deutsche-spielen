import pytest

from app.domain.sentence_validation import validate_sentence


# --- Check: non_empty ---

def test_empty_sentence_fails():
    result = validate_sentence("", ["spielen", "dem Freund", "am Montag"], "A")
    assert not result.is_valid
    assert "non_empty" in result.checks_failed


def test_whitespace_only_fails():
    result = validate_sentence("   ", ["spielen", "dem Freund", "am Montag"], "A")
    assert not result.is_valid
    assert "non_empty" in result.checks_failed


# --- Check: punctuation ---

@pytest.mark.parametrize("ending", [".", "?", "!"])
def test_valid_punctuation(ending):
    result = validate_sentence(
        f"Der Lehrer spielt am Montag{ending}",
        ["spielen", "Lehrer", "am Montag"], "A"
    )
    assert "punctuation" in result.checks_passed


def test_missing_punctuation_fails():
    result = validate_sentence(
        "Der Lehrer spielt am Montag",
        ["spielen", "Lehrer", "am Montag"], "A"
    )
    assert "punctuation" in result.checks_failed


# --- Check: contains_suggestions ---

def test_suggestion_tokens_present():
    result = validate_sentence(
        "Peter spielt am Montag Fußball.",
        ["spielen", "dem Freund", "am Montag"], "A"
    )
    assert "contains_suggestions" in result.checks_passed


def test_suggestion_tokens_missing():
    result = validate_sentence(
        "Es ist ein schöner Tag.",
        ["spielen", "dem Freund", "am Montag"], "A"
    )
    assert "contains_suggestions" in result.checks_failed


def test_suggestion_tokens_case_insensitive():
    result = validate_sentence(
        "SPIELEN macht Spaß. Am Montag auch.",
        ["spielen", "dem Freund", "am Montag"], "A"
    )
    assert "contains_suggestions" in result.checks_passed


# --- Check: sentence_type_hint per letter ---

def test_type_A_hauptsatz_passes():
    result = validate_sentence("Der Hund spielt im Garten.", ["spielen", "Hund", "Garten"], "A")
    assert "sentence_type_hint" in result.checks_passed


def test_type_A_starting_with_weil_fails():
    result = validate_sentence("Weil der Hund spielt.", ["spielen", "Hund", "weil"], "A")
    assert "sentence_type_hint" in result.checks_failed


def test_type_B_nebensatz_with_conjunction_passes():
    result = validate_sentence("Ich lerne, weil das wichtig ist.", ["lerne", "wichtig", "ist"], "B")
    assert "sentence_type_hint" in result.checks_passed


def test_type_B_no_conjunction_fails():
    result = validate_sentence("Der Hund spielt im Garten.", ["spielen", "Hund", "Garten"], "B")
    assert "sentence_type_hint" in result.checks_failed


def test_type_C_question_with_mark_passes():
    result = validate_sentence("Wann spielt der Hund?", ["spielen", "Hund", "wann"], "C")
    assert "sentence_type_hint" in result.checks_passed


def test_type_C_no_question_mark_fails():
    result = validate_sentence("Wann spielt der Hund.", ["spielen", "Hund", "wann"], "C")
    assert "sentence_type_hint" in result.checks_failed


def test_type_D_infinitiv_zu_passes():
    result = validate_sentence("Er versucht, das Buch zu lesen.", ["lesen", "Buch", "versucht"], "D")
    assert "sentence_type_hint" in result.checks_passed


def test_type_D_no_zu_fails():
    result = validate_sentence("Er liest das Buch.", ["lesen", "Buch", "versucht"], "D")
    assert "sentence_type_hint" in result.checks_failed


def test_type_E_perfekt_passes():
    result = validate_sentence("Er hat das Buch gelesen.", ["lesen", "Buch", "er"], "E")
    assert "sentence_type_hint" in result.checks_passed


def test_type_E_futur_passes():
    result = validate_sentence("Er wird das Buch lesen.", ["lesen", "Buch", "er"], "E")
    assert "sentence_type_hint" in result.checks_passed


def test_type_E_no_auxiliary_fails():
    result = validate_sentence("Er liest das Buch.", ["lesen", "Buch", "er"], "E")
    assert "sentence_type_hint" in result.checks_failed


def test_type_F_possessivartikel_passes():
    result = validate_sentence("Mein Bruder spielt Fußball.", ["spielen", "Bruder", "Fußball"], "F")
    assert "sentence_type_hint" in result.checks_passed


def test_type_F_no_possessive_fails():
    result = validate_sentence("Der Bruder spielt Fußball.", ["spielen", "Bruder", "Fußball"], "F")
    assert "sentence_type_hint" in result.checks_failed


# --- Overall is_valid ---

def test_fully_valid_sentence():
    result = validate_sentence(
        "Mein Bruder hat dem Freund ein Buch gegeben.",
        ["geben", "dem Freund", "ein Buch"], "E"
    )
    assert result.is_valid
    assert not result.checks_failed


def test_message_is_present():
    result = validate_sentence("", [], "A")
    assert result.message
