import random
from dataclasses import dataclass


@dataclass(frozen=True)
class NumericDieResult:
    value: int        # 1-6
    label: str        # e.g. "Subjekt"
    question: str     # e.g. "Wer?"
    suggestion: str   # random pick from vocab pool


@dataclass(frozen=True)
class SentenceTypeDieResult:
    letter: str   # A-F
    label: str    # e.g. "Hauptsatz"


def roll_three_unique(rng: random.Random | None = None) -> tuple[int, int, int]:
    """Return 3 distinct values each in range 1-6."""
    r = rng or random
    values = r.sample(range(1, 7), 3)
    return values[0], values[1], values[2]


def roll_sentence_type(rng: random.Random | None = None) -> str:
    """Return a random letter A-F."""
    r = rng or random
    return r.choice("ABCDEF")
