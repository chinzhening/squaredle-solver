"""What Squaredle made of the words a run submitted.

Read from the solution blob in localStorage, which records accepted words by
identity rather than as a running count - so one read after typing is correct
whenever each write happened to land.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

# "squaredle-2026/08/17-solution", or "-xp-solution" for XP. A shape check only;
# the board is selected where the keys are read.
SOLUTION_KEY_RE = re.compile(r"^squaredle-\d{4}/\d{2}/\d{2}(?:-xp)?-solution$")


@dataclass(frozen=True)
class SolutionState:
    """Squaredle's own record of a puzzle.

    `key` is verbatim: the date it names runs a day ahead of the share text for
    the same puzzle, so it is recorded rather than interpreted. Words are stored
    lowercase and kept that way.
    """

    key: str
    words: frozenset[str]
    obscure_words: frozenset[str]
    non_word_count: int | None


@dataclass
class WordOutcomes:
    """Submitted words Squaredle credited.

    Free of Playwright and pymongo so the client and the writers can both
    depend on it.

    `total_credited_words` and `non_word_count` are Squaredle's own tallies,
    stored unjudged so check_totals stays reproducible from the document.
    """

    accepted: list[str] = field(default_factory=list)
    bonus: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    solution_key: str | None = None
    total_credited_words: int = 0
    non_word_count: int | None = None

    def as_document(self) -> dict[str, Any]:
        """Flatten for storage, nested under one key by the caller."""
        return {
            "accepted": self.accepted,
            "bonus": self.bonus,
            "rejected": self.rejected,
            "accepted_count": len(self.accepted),
            "bonus_count": len(self.bonus),
            "rejected_count": len(self.rejected),
            "total_credited_words": self.total_credited_words,
            "non_word_count": self.non_word_count,
            "solution_key": self.solution_key,
        }


def _word_set(value: Any) -> frozenset[str]:
    """Lowercased words from a stored list, ignoring anything not a string."""
    if not isinstance(value, list):
        return frozenset()
    return frozenset(item.lower() for item in value if isinstance(item, str))


def parse_solution(key: str, raw: str) -> SolutionState | None:
    """Build a SolutionState from a localStorage key and its JSON value.

    None rather than raising: a changed format should cost the measurement, not
    the run.
    """
    if SOLUTION_KEY_RE.match(key) is None:
        return None

    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        logging.warning(f"Solution value for {key} is not JSON")
        return None

    if not isinstance(payload, dict):
        logging.warning(f"Solution value for {key} is not an object")
        return None

    non_word_count = payload.get("nonWordCount")

    return SolutionState(
        key=key,
        words=_word_set(payload.get("words")),
        obscure_words=_word_set(payload.get("obscureWords")),
        # bool is an int subclass, so it has to be excluded explicitly.
        non_word_count=(
            non_word_count
            if isinstance(non_word_count, int) and not isinstance(non_word_count, bool)
            else None
        ),
    )


def classify(submitted: list[str], state: SolutionState) -> WordOutcomes:
    """Bucket submitted words against the puzzle's recorded state.

    A word credited before this run still counts as accepted: Squaredle's
    dictionary contains it either way, which is what is being measured.
    """
    outcomes = WordOutcomes(
        solution_key=state.key,
        total_credited_words=len(state.words) + len(state.obscure_words),
        non_word_count=state.non_word_count,
    )

    for word in submitted:
        key = word.lower()
        if key in state.words:
            outcomes.accepted.append(word)
        elif key in state.obscure_words:
            outcomes.bonus.append(word)
        else:
            outcomes.rejected.append(word)

    check_totals(len(submitted), outcomes)
    return outcomes


def check_totals(submitted: int, outcomes: WordOutcomes) -> bool | None:
    """Whether Squaredle's tallies add up to the number of words submitted.

    On a fresh board every submission is either credited or counted a non-word,
    so the two sum to what was sent. The direction of a mismatch diagnoses it:

    - short: a write had not landed, so a credited word reads as rejected. The
      one failure a single end-read cannot rule out by itself.
    - over: words credited that this run never sent - a reveal, or a board
      already part-played.

    None when there was no tally to check against.
    """
    if outcomes.non_word_count is None:
        return None

    total = outcomes.total_credited_words + outcomes.non_word_count
    if total == submitted:
        return True

    logging.warning(
        f"Squaredle tallies {total} submissions "
        f"({'short of' if total < submitted else 'over'} the {submitted} sent): "
        f"{outcomes.total_credited_words} credited + "
        f"{outcomes.non_word_count} non-words"
    )
    return False
