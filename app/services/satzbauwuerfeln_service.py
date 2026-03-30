import random
from dataclasses import dataclass

from app.domain.dice import (
    NumericDieResult,
    SentenceTypeDieResult,
    roll_sentence_type,
    roll_three_unique,
)
from app.domain.satzbauwuerfeln_rules import resolve_numeric_die, resolve_sentence_type


@dataclass(frozen=True)
class RollResult:
    dice: list[NumericDieResult]          # 3 items, one per numeric die
    sentence_type: SentenceTypeDieResult  # A-F die


def perform_roll(rng: random.Random | None = None) -> RollResult:
    """Roll all dice and return resolved results."""
    d1, d2, d3 = roll_three_unique(rng)
    dice = [
        resolve_numeric_die(d1, rng),
        resolve_numeric_die(d2, rng),
        resolve_numeric_die(d3, rng),
    ]
    sentence_type = resolve_sentence_type(roll_sentence_type(rng))
    return RollResult(dice=dice, sentence_type=sentence_type)
