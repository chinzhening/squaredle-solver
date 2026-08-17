"""Tests for the share-text parsers.

Samples are real. Add new ones rather than editing one: a rewritten sample
cannot catch the day the format drifts.
"""

from datetime import UTC, date, datetime

import pytest

from squaredle.share import (
    WordCounts,
    parse_puzzle_date,
    parse_word_counts,
    puzzle_date_from_run,
    puzzle_day_of,
)

# Captured 2026-08-16.
SAMPLE_2026_08_16 = """I played https://squaredle.com 08/16:
*68/68 words (+86 bonus words)
📖 Top player by bonus words
🔥 Solve streak: 1"""


class TestPuzzleDayOf:
    def test_before_turnover_is_the_previous_puzzle(self) -> None:
        """Real run: solved_at 2026-08-04 07:36 UTC, share text 08/03."""
        assert puzzle_day_of(datetime(2026, 8, 4, 7, 36, tzinfo=UTC)) == date(
            2026, 8, 3
        )

    def test_after_turnover_is_the_current_puzzle(self) -> None:
        assert puzzle_day_of(datetime(2026, 8, 4, 13, 54, tzinfo=UTC)) == date(
            2026, 8, 4
        )

    def test_turnover_boundary(self) -> None:
        assert puzzle_day_of(datetime(2026, 8, 4, 9, 59, tzinfo=UTC)) == date(
            2026, 8, 3
        )
        assert puzzle_day_of(datetime(2026, 8, 4, 10, 0, tzinfo=UTC)) == date(
            2026, 8, 4
        )

    def test_naive_is_taken_as_utc(self) -> None:
        naive = datetime(2026, 8, 4, 13, 54)
        assert puzzle_day_of(naive) == puzzle_day_of(naive.replace(tzinfo=UTC))


class TestParsePuzzleDate:
    def test_reads_the_date_beside_the_url(self) -> None:
        parsed = parse_puzzle_date(SAMPLE_2026_08_16, date(2026, 8, 16))
        assert parsed == date(2026, 8, 16)

    def test_does_not_match_the_word_tally(self) -> None:
        """An unanchored pattern reads "*68/68 words" as June 8th."""
        parsed = parse_puzzle_date(SAMPLE_2026_08_16, date(2026, 8, 16))
        assert parsed != date(2026, 6, 8)

    def test_year_comes_from_the_reference(self) -> None:
        text = "I played https://squaredle.com 03/04:"
        assert parse_puzzle_date(text, date(2024, 3, 4)) == date(2024, 3, 4)

    def test_december_puzzle_referenced_from_january(self) -> None:
        text = "I played https://squaredle.com 12/31:"
        assert parse_puzzle_date(text, date(2027, 1, 1)) == date(2026, 12, 31)

    def test_january_puzzle_referenced_from_december(self) -> None:
        text = "I played https://squaredle.com 01/01:"
        assert parse_puzzle_date(text, date(2026, 12, 31)) == date(2027, 1, 1)

    def test_explicit_year_wins_over_the_reference(self) -> None:
        text = "I played https://squaredle.com 08/16/25:"
        assert parse_puzzle_date(text, date(2026, 8, 16)) == date(2025, 8, 16)

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "I played squaredle today!",
            "*68/68 words (+86 bonus words)",
        ],
    )
    def test_returns_none_rather_than_raising(self, text: str) -> None:
        assert parse_puzzle_date(text, date(2026, 8, 16)) is None

    def test_impossible_date_is_rejected(self) -> None:
        text = "I played https://squaredle.com 02/30:"
        assert parse_puzzle_date(text, date(2026, 2, 28)) is None


class TestPuzzleDateFromRun:
    def test_resolves_the_year_across_new_year(self) -> None:
        """23:00 UTC on 31 Dec is already the 01/01 puzzle, one year on."""
        text = "I played https://squaredle.com 01/01:"
        assert puzzle_date_from_run(text, datetime(2026, 12, 31, 23, 0)) == date(
            2027, 1, 1
        )

    def test_matches_the_real_2026_08_16_run(self) -> None:
        assert puzzle_date_from_run(
            SAMPLE_2026_08_16, datetime(2026, 8, 16, 10, 50)
        ) == date(2026, 8, 16)

    def test_empty_share_text_is_none(self) -> None:
        assert puzzle_date_from_run("", datetime(2026, 8, 16, 10, 50)) is None


class TestParseWordCounts:
    def test_reads_required_and_bonus(self) -> None:
        assert parse_word_counts(SAMPLE_2026_08_16) == WordCounts(
            found=68, total=68, bonus=86
        )

    def test_bonus_defaults_to_zero_when_absent(self) -> None:
        assert parse_word_counts("*12/68 words") == WordCounts(
            found=12, total=68, bonus=0
        )

    def test_returns_none_rather_than_raising(self) -> None:
        assert parse_word_counts("") is None
