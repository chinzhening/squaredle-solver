"""Tests for the solution blob and word-outcome classification."""

import json

import pytest

from squaredle.results import SolutionState, check_totals, classify, parse_solution

# Captured 2026-08-17, mid-game.
SAMPLE_KEY = "squaredle-2026/08/17-solution"
SAMPLE_VALUE = json.dumps(
    {
        "puzzleVersion": None,
        "words": ["goal", "host", "most", "time", "mite", "might"],
        "obscureWords": ["calo", "lite"],
        "nonWordCount": 12,
        "hints": {"sort": False, "firstLetters": False},
        "everEnabledHints": False,
        "ms": 830455,
        "shared": False,
        "revealsUsed": 1,
        "rotations": 0,
    }
)


def _state(
    words: set[str] | None = None,
    obscure: set[str] | None = None,
    non_word_count: int | None = 0,
) -> SolutionState:
    return SolutionState(
        key=SAMPLE_KEY,
        words=frozenset(words or set()),
        obscure_words=frozenset(obscure or set()),
        non_word_count=non_word_count,
    )


class TestParseSolution:
    def test_reads_the_real_sample(self) -> None:
        state = parse_solution(SAMPLE_KEY, SAMPLE_VALUE)
        assert state is not None
        assert state.key == SAMPLE_KEY
        assert state.words == frozenset(
            {"goal", "host", "most", "time", "mite", "might"}
        )
        assert state.obscure_words == frozenset({"calo", "lite"})
        assert state.non_word_count == 12

    def test_the_xp_key_form_is_accepted(self) -> None:
        """Shape only -- the mode is selected where the keys are read."""
        key = "squaredle-2026/08/17-xp-solution"
        state = parse_solution(key, SAMPLE_VALUE)
        assert state is not None
        assert state.key == key

    def test_words_are_lowercased(self) -> None:
        state = parse_solution(SAMPLE_KEY, json.dumps({"words": ["GOAL", "Host"]}))
        assert state is not None
        assert state.words == frozenset({"goal", "host"})

    @pytest.mark.parametrize(
        "key",
        [
            "squaredle-2026/08/17",  # no -solution suffix
            "squaredle-2026-08-17-solution",  # dashes, not slashes
            "squaredle-2026/08/17-daily-solution",  # unknown mode segment
            "settings",
            "",
        ],
    )
    def test_unrecognised_keys_are_none(self, key: str) -> None:
        assert parse_solution(key, SAMPLE_VALUE) is None

    @pytest.mark.parametrize("raw", ["", "not json", "[1, 2, 3]", "null", '"text"'])
    def test_unusable_values_are_none(self, raw: str) -> None:
        assert parse_solution(SAMPLE_KEY, raw) is None

    def test_missing_fields_default_to_empty(self) -> None:
        state = parse_solution(SAMPLE_KEY, "{}")
        assert state is not None
        assert state.words == frozenset()
        assert state.obscure_words == frozenset()
        assert state.non_word_count is None

    def test_non_integer_tally_is_none(self) -> None:
        state = parse_solution(SAMPLE_KEY, json.dumps({"nonWordCount": "12"}))
        assert state is not None
        assert state.non_word_count is None

    def test_boolean_tally_is_not_taken_as_an_integer(self) -> None:
        """bool subclasses int, so it needs excluding explicitly."""
        state = parse_solution(SAMPLE_KEY, json.dumps({"nonWordCount": True}))
        assert state is not None
        assert state.non_word_count is None

    def test_non_string_words_are_skipped(self) -> None:
        state = parse_solution(SAMPLE_KEY, json.dumps({"words": ["goal", 7, None]}))
        assert state is not None
        assert state.words == frozenset({"goal"})


class TestClassify:
    def test_splits_required_bonus_and_rejected(self) -> None:
        state = _state(words={"goal", "host"}, obscure={"calo"})
        outcomes = classify(["GOAL", "HOST", "CALO", "ZZZZ"], state)

        assert outcomes.accepted == ["GOAL", "HOST"]
        assert outcomes.bonus == ["CALO"]
        assert outcomes.rejected == ["ZZZZ"]

    def test_reports_the_submitted_casing(self) -> None:
        """Storage is lowercase; the document should match the solver's output."""
        assert classify(["GOAL"], _state(words={"goal"})).accepted == ["GOAL"]

    def test_preserves_submission_order(self) -> None:
        outcomes = classify(["CCCC", "AAAA"], _state(words={"aaaa", "cccc"}))
        assert outcomes.accepted == ["CCCC", "AAAA"]

    def test_credited_words_never_submitted_are_ignored(self) -> None:
        """A revealed word is in the stored set but was not offered."""
        outcomes = classify(["GOAL"], _state(words={"goal", "revealed"}))
        assert outcomes.accepted == ["GOAL"]
        assert outcomes.rejected == []

    def test_a_rerun_credits_already_found_words(self) -> None:
        """Resubmitting a found word does not mutate state, and is not a miss."""
        outcomes = classify(["GOAL", "HOST"], _state(words={"goal", "host"}))
        assert outcomes.accepted == ["GOAL", "HOST"]
        assert outcomes.rejected == []

    def test_carries_the_tallies_through_unjudged(self) -> None:
        state = _state(words={"goal", "host"}, obscure={"calo"}, non_word_count=12)
        outcomes = classify(["GOAL"], state)

        assert outcomes.total_credited_words == 3
        assert outcomes.non_word_count == 12

    def test_a_missing_tally_stays_none(self) -> None:
        outcomes = classify(["GOAL"], _state(words={"goal"}, non_word_count=None))
        assert outcomes.non_word_count is None

    def test_records_the_key_verbatim_rather_than_a_date(self) -> None:
        """The key runs a day ahead of the share text; recorded, not adopted."""
        outcomes = classify(["GOAL"], _state(words={"goal"}))
        assert outcomes.solution_key == SAMPLE_KEY


class TestCheckTotals:
    def test_true_when_the_tallies_account_for_every_submission(self) -> None:
        state = _state(words={"goal", "host"}, obscure={"calo"}, non_word_count=1)
        assert check_totals(4, classify(["GOAL", "HOST", "CALO", "ZZZZ"], state))

    def test_false_when_short__a_write_had_not_landed(self) -> None:
        """The one failure a single end-read cannot rule out by itself."""
        state = _state(words={"goal"}, non_word_count=0)
        assert check_totals(2, classify(["GOAL", "HOST"], state)) is False

    def test_false_when_over__revealed_or_part_played(self) -> None:
        state = _state(words={"goal", "revealed"}, non_word_count=0)
        assert check_totals(1, classify(["GOAL"], state)) is False

    def test_none_without_a_tally_to_check_against(self) -> None:
        state = _state(words={"goal"}, non_word_count=None)
        assert check_totals(1, classify(["GOAL"], state)) is None

    def test_counts_every_credited_word_not_just_submitted_ones(self) -> None:
        """accepted_count would miss a revealed word; the tally does not."""
        state = _state(words={"goal", "revealed"}, non_word_count=0)
        outcomes = classify(["GOAL"], state)

        assert len(outcomes.accepted) == 1
        assert outcomes.total_credited_words == 2


class TestAsDocument:
    def test_carries_lists_counts_and_the_tally(self) -> None:
        state = _state(words={"goal"}, obscure={"calo"}, non_word_count=1)
        outcomes = classify(["GOAL", "CALO", "ZZZZ"], state)

        assert outcomes.as_document() == {
            "accepted": ["GOAL"],
            "bonus": ["CALO"],
            "rejected": ["ZZZZ"],
            "accepted_count": 1,
            "bonus_count": 1,
            "rejected_count": 1,
            "total_credited_words": 2,
            "non_word_count": 1,
            "solution_key": SAMPLE_KEY,
        }
