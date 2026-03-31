import pytest

from app.domain.sentence_validation import validate_sentence
from app.services.grammar_service import GrammarIssue


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


@pytest.mark.parametrize("letter", ["A", "B", "D", "E", "F"])
def test_non_question_types_with_question_mark_fail(letter):
    result = validate_sentence(
        "Um 8 Uhr habe ich mit meinen Freunden eine Pizza gegessen?",
        ["Pizza", "Freunden", "8 Uhr"],
        letter,
    )
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


# --- Check: lightweight German word order ---

def test_word_order_fronted_time_with_finite_verb_passes():
    result = validate_sentence(
        "Um 8 Uhr habe ich mit meinen Freunden eine Pizza gegessen.",
        ["Pizza", "Freunden", "8 Uhr"],
        "A",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_fronted_time_without_finite_verb_fails():
    result = validate_sentence(
        "Um 8 Uhr ich mit meinen Freunden eine Pizza gegessen.",
        ["Pizza", "Freunden", "8 Uhr"],
        "A",
    )
    assert "word_order_hint" in result.checks_failed


def test_nebensatz_finite_verb_at_end_passes():
    result = validate_sentence(
        "Weil ich gestern krank war.",
        ["gestern", "krank", "war"],
        "B",
    )
    assert "word_order_hint" in result.checks_passed


def test_nebensatz_wrong_verb_position_fails():
    result = validate_sentence(
        "Weil ich war gestern krank.",
        ["gestern", "krank", "war"],
        "B",
    )
    assert "word_order_hint" in result.checks_failed


# -- Word order: type A (Hauptsatz) additional cases --

def test_word_order_subject_first_passes():
    # Subject-verb-object: verb at index 1 (V2)
    result = validate_sentence(
        "Ich spiele jeden Tag Fußball.",
        ["spielen", "Fußball", "Tag"],
        "A",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_fronted_adverb_passes():
    # Fronted adverb → inversion: verb at index 2
    result = validate_sentence(
        "Gestern habe ich Fußball gespielt.",
        ["spielen", "Fußball", "gestern"],
        "A",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_verb_too_late_fails():
    # Verb buried too deep (index 5+)
    result = validate_sentence(
        "Ich gestern am Abend mit Freunden spielte.",
        ["spielen", "Freunden", "gestern"],
        "A",
    )
    assert "word_order_hint" in result.checks_failed


# -- Word order: type C (Fragesatz) --

def test_word_order_verb_first_question_passes():
    # Verb-first yes/no question: finite at index 0
    result = validate_sentence(
        "Spielst du heute Fußball?",
        ["spielen", "Fußball", "heute"],
        "C",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_W_question_passes():
    # W-question: question word at 0, finite verb at 1
    result = validate_sentence(
        "Wann spielst du Fußball?",
        ["spielen", "Fußball", "wann"],
        "C",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_question_verb_too_late_fails():
    # Verb pushed past position 2 in a Fragesatz
    result = validate_sentence(
        "Wann du Fußball spielst?",
        ["spielen", "Fußball", "wann"],
        "C",
    )
    assert "word_order_hint" in result.checks_failed


# -- Word order: type B (Nebensatz) additional cases --

def test_nebensatz_weil_verb_at_end_passes():
    # Pure Nebensatz starting with conjunction — finite verb must be near end
    result = validate_sentence(
        "Weil er morgen nach Berlin fährt.",
        ["fahren", "morgen", "Berlin"],
        "B",
    )
    assert "word_order_hint" in result.checks_passed


def test_nebensatz_obwohl_verb_at_end_passes():
    result = validate_sentence(
        "Obwohl er sehr müde ist.",
        ["sein", "müde", "obwohl"],
        "B",
    )
    assert "word_order_hint" in result.checks_passed


def test_nebensatz_waehrend_wrong_verb_position_fails():
    # Finite verb "hat" at index 2 instead of near end
    result = validate_sentence(
        "Während er hat seinen Kaffee getrunken.",
        ["Kaffee", "trinken", "während"],
        "B",
    )
    assert "word_order_hint" in result.checks_failed


# -- Word order: type E (Perfekt / Futur) --

def test_word_order_perfekt_passes():
    result = validate_sentence(
        "Ich habe gestern Fußball gespielt.",
        ["spielen", "Fußball", "gestern"],
        "E",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_futur_passes():
    result = validate_sentence(
        "Sie wird morgen kommen.",
        ["kommen", "morgen", "werden"],
        "E",
    )
    assert "word_order_hint" in result.checks_passed


# -- Word order: type F (Possessivartikel) --

def test_word_order_possessive_subject_first_passes():
    result = validate_sentence(
        "Meine Schwester spielt Gitarre.",
        ["spielen", "Schwester", "Gitarre"],
        "F",
    )
    assert "word_order_hint" in result.checks_passed


def test_word_order_possessive_fronted_obj_passes():
    result = validate_sentence(
        "Seinen Bruder hat er nie gesehen.",
        ["sehen", "Bruder", "sein"],
        "F",
    )
    assert "word_order_hint" in result.checks_passed


# -- Sentence type: additional edge cases --

def test_type_B_nachdem_passes():
    result = validate_sentence(
        "Nachdem ich gegessen hatte, ging ich schlafen.",
        ["schlafen", "essen", "nachdem"],
        "B",
    )
    assert "sentence_type_hint" in result.checks_passed


def test_type_B_damit_passes():
    result = validate_sentence(
        "Ich lerne Deutsch, damit ich in Deutschland arbeiten kann.",
        ["lernen", "Deutsch", "damit"],
        "B",
    )
    assert "sentence_type_hint" in result.checks_passed


def test_type_D_zu_infinitive_at_end_passes():
    # Uses explicit " zu " with spaces (trennbare Verben like aufzustehen are not detected)
    result = validate_sentence(
        "Sie hofft, das Buch morgen zu lesen.",
        ["hoffen", "Buch", "morgen"],
        "D",
    )
    assert "sentence_type_hint" in result.checks_passed


def test_type_E_had_auxiliary_modal_passes():
    result = validate_sentence(
        "Er hat das Paket abholen müssen.",
        ["abholen", "Paket", "müssen"],
        "E",
    )
    assert "sentence_type_hint" in result.checks_passed


def test_type_F_dein_possessive_passes():
    result = validate_sentence(
        "Dein Hund ist sehr süß.",
        ["sein", "Hund", "süß"],
        "F",
    )
    assert "sentence_type_hint" in result.checks_passed


def test_type_F_ihr_possessive_passes():
    result = validate_sentence(
        "Ihr Auto steht vor dem Haus.",
        ["stehen", "Auto", "Haus"],
        "F",
    )
    assert "sentence_type_hint" in result.checks_passed


# -- contains_suggestions: edge cases --

def test_suggestion_stem_match_passes():
    # "spielen" should match "spielt" via 4-char prefix heuristic
    result = validate_sentence(
        "Er spielt jeden Tag Tennis.",
        ["spielen", "Tennis", "Tag"],
        "A",
    )
    assert "contains_suggestions" in result.checks_passed


def test_only_one_suggestion_matched_fails():
    result = validate_sentence(
        "Der Hund schläft.",
        ["spielen", "dem Freund", "am Montag"],
        "A",
    )
    assert "contains_suggestions" in result.checks_failed


def test_suggestion_stop_word_only_skipped():
    # "am" is a stop word, so it doesn't count toward the match
    result = validate_sentence(
        "Ich laufe am Morgen.",
        ["am", "laufen", "Morgen"],
        "A",
    )
    # "laufen" and "Morgen" are non-stop-words and should match
    assert "contains_suggestions" in result.checks_passed


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


def test_grammar_errors_are_non_blocking(monkeypatch):
    def fake_check_grammar(sentence: str):
        return [
            GrammarIssue(
                message="Möglicher Grammatikfehler.",
                rule_id="FAKE_RULE",
                offset=0,
                length=4,
            )
        ]

    monkeypatch.setattr("app.domain.sentence_validation.check_grammar", fake_check_grammar)
    result = validate_sentence(
        "Mein Bruder hat dem Freund ein Buch gegeben.",
        ["geben", "dem Freund", "ein Buch"],
        "E",
    )

    assert result.is_valid is True
    assert "grammar_errors" in result.checks_failed
    assert result.grammar_errors
