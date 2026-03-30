import json
import random
from pathlib import Path

from app.domain.dice import NumericDieResult, SentenceTypeDieResult

_VOCAB_PATH = Path(__file__).resolve().parent.parent / "data" / "vocab.json"

SENTENCE_TYPE_LABELS: dict[str, str] = {
    "A": "Hauptsatz",
    "B": "Nebensatz",
    "C": "Fragesatz",
    "D": "Satz mit Infinitiv + zu",
    "E": "Perfekt oder Futur",
    "F": "Satz mit Possessivartikel",
}


def _load_vocab() -> dict:
    with _VOCAB_PATH.open(encoding="utf-8") as f:
        return json.load(f)


_VOCAB: dict = _load_vocab()


def resolve_numeric_die(value: int, rng: random.Random | None = None) -> NumericDieResult:
    """Map a die value (1-6) to its category and pick a random suggestion."""
    entry = _VOCAB[str(value)]
    r = rng or random
    suggestion = r.choice(entry["suggestions"])
    return NumericDieResult(
        value=value,
        label=entry["label"],
        question=entry["question"],
        suggestion=suggestion,
    )


def resolve_sentence_type(letter: str) -> SentenceTypeDieResult:
    """Map a letter A-F to its sentence type label."""
    return SentenceTypeDieResult(
        letter=letter,
        label=SENTENCE_TYPE_LABELS[letter],
    )
