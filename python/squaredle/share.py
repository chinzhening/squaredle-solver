"""Parse the fields Squaredle exposes only in its share text.

The share text is stored verbatim and everything here is derived from it, so
parsers return None rather than raising: a drifted format must not cost a run
its result, and a fixed parser can always be re-run over history.
"""

import logging
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

# Squaredle turns over at 10:00 UTC (6pm UTC+8), not at any midnight.
PUZZLE_DAY_START_UTC = timedelta(hours=10)

# Anchored to the domain, not a bare `M/D`: the next line reads
# "*68/68 words (+86 bonus words)", which a loose pattern reads as June 8th.
# The TLD varies -- the share text says .com, the page we scrape is .app. The
# year group is never present today; it is here so a format that starts
# supplying one is used rather than ignored.
_PUZZLE_DATE_RE = re.compile(
    r"squaredle\.[a-z]+\s+(?P<month>\d{1,2})/(?P<day>\d{1,2})"
    r"(?:/(?P<year>\d{2,4}))?",
    re.IGNORECASE,
)

# "*68/68 words (+86 bonus words)". The leading marker flags a complete solve
# and varies, so it is left out of the match.
_WORD_COUNTS_RE = re.compile(
    r"(?P<found>\d+)\s*/\s*(?P<total>\d+)\s+words"
    r"(?:\s*\(\+\s*(?P<bonus>\d+)\s+bonus\s+words?\))?",
    re.IGNORECASE,
)

_MAX_PLAUSIBLE_DRIFT_DAYS = 2


@dataclass(frozen=True)
class WordCounts:
    """Words the game credited: `found`/`total` are required, `bonus` extra.

    found + bonus is everything Squaredle accepted, so subtracting it from the
    number submitted gives how many its dictionary rejected.
    """

    found: int
    total: int
    bonus: int


def puzzle_day_of(instant: datetime) -> date:
    """Which puzzle was current at a given moment.

    Naive instants are taken as UTC, which is what datetime.now(UTC) and a
    Mongo round-trip both hand back.
    """
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=UTC)
    return (instant.astimezone(UTC) - PUZZLE_DAY_START_UTC).date()


def _resolve_year(month: int, reference: date) -> int:
    """Supply the year the share text omits.

    Both New Year directions are reachable, since a puzzle day straddles two
    calendar days.
    """
    if month == 12 and reference.month == 1:
        return reference.year - 1
    if month == 1 and reference.month == 12:
        return reference.year + 1
    return reference.year


def parse_puzzle_date(share_text: str, reference: date) -> date | None:
    """Extract which puzzle a share text belongs to.

    `reference` is the puzzle day the text is expected to be on, normally
    puzzle_day_of(solved_at). It supplies the omitted year and anchors the
    sanity check.
    """
    match = _PUZZLE_DATE_RE.search(share_text)
    if match is None:
        logging.warning("No puzzle date found in share text")
        return None

    month = int(match.group("month"))
    day = int(match.group("day"))

    raw_year = match.group("year")
    if raw_year is None:
        year = _resolve_year(month, reference)
    else:
        year = int(raw_year)
        if year < 100:
            year += 2000

    try:
        puzzle_date = date(year, month, day)
    except ValueError:
        logging.warning(f"Share text gave an impossible date: {month}/{day}/{year}")
        return None

    drift = abs((puzzle_date - reference).days)
    if drift > _MAX_PLAUSIBLE_DRIFT_DAYS:
        # Returned anyway: a flagged value the caller can audit beats a silent
        # None, and the caller records where the value came from.
        logging.warning(
            f"Puzzle date {puzzle_date} is {drift} days from the expected "
            f"puzzle day {reference} -- check the parse"
        )

    return puzzle_date


def puzzle_date_from_run(share_text: str, solved_at: datetime) -> date | None:
    """Which puzzle a run was playing, from its share text and when it ran."""
    if not share_text:
        return None
    return parse_puzzle_date(share_text, puzzle_day_of(solved_at))


def parse_word_counts(share_text: str) -> WordCounts | None:
    """Extract the word tallies Squaredle credited for a puzzle."""
    match = _WORD_COUNTS_RE.search(share_text)
    if match is None:
        logging.warning("No word counts found in share text")
        return None

    raw_bonus = match.group("bonus")
    return WordCounts(
        found=int(match.group("found")),
        total=int(match.group("total")),
        bonus=0 if raw_bonus is None else int(raw_bonus),
    )
