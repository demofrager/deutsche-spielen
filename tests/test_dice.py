import random

import pytest

from app.domain.dice import roll_sentence_type, roll_three_unique
from app.domain.satzbauwuerfeln_rules import (
    SENTENCE_TYPE_LABELS,
    resolve_numeric_die,
    resolve_sentence_type,
)
from app.services.satzbauwuerfeln_service import perform_roll


# --- dice.py ---

def test_roll_three_unique_are_distinct():
    for _ in range(50):
        a, b, c = roll_three_unique()
        assert len({a, b, c}) == 3


def test_roll_three_unique_in_range():
    for _ in range(50):
        for v in roll_three_unique():
            assert 1 <= v <= 6


def test_roll_three_unique_seeded():
    rng = random.Random(42)
    result = roll_three_unique(rng)
    assert len(set(result)) == 3


def test_roll_sentence_type_valid():
    for _ in range(50):
        letter = roll_sentence_type()
        assert letter in "ABCDEF"


# --- satzbauwuerfeln_rules.py ---

@pytest.mark.parametrize("value,expected_label", [
    (1, "Subjekt"),
    (2, "Verb"),
    (3, "Akkusativobjekt"),
    (4, "Dativobjekt"),
    (5, "Lokalangabe"),
    (6, "Temporalangabe"),
])
def test_resolve_numeric_die_label(value, expected_label):
    result = resolve_numeric_die(value)
    assert result.value == value
    assert result.label == expected_label
    assert result.question
    assert result.suggestion


def test_resolve_numeric_die_suggestion_comes_from_pool():
    from app.domain.satzbauwuerfeln_rules import _VOCAB
    for value in range(1, 7):
        result = resolve_numeric_die(value)
        assert result.suggestion in _VOCAB[str(value)]["suggestions"]


@pytest.mark.parametrize("letter,expected_label", list(SENTENCE_TYPE_LABELS.items()))
def test_resolve_sentence_type(letter, expected_label):
    result = resolve_sentence_type(letter)
    assert result.letter == letter
    assert result.label == expected_label


# --- satzbauwuerfeln_service.py ---

def test_perform_roll_structure():
    result = perform_roll()
    assert len(result.dice) == 3
    values = [d.value for d in result.dice]
    assert len(set(values)) == 3
    assert result.sentence_type.letter in "ABCDEF"


def test_perform_roll_seeded_is_deterministic():
    rng = random.Random(99)
    r1 = perform_roll(rng)
    rng = random.Random(99)
    r2 = perform_roll(rng)
    assert [d.value for d in r1.dice] == [d.value for d in r2.dice]
    assert r1.sentence_type.letter == r2.sentence_type.letter
