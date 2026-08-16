"""Fixture tests for the C++ solver binary."""

from pathlib import Path

import pytest

from squaredle.board import BoardInfo
from squaredle.config import PROJECT_ROOT
from squaredle.solver import solve

FIXTURE_DIR = PROJECT_ROOT / "tests" / "boards"
FIXTURES = sorted(FIXTURE_DIR.glob("*.in"))


def _case_id(path: Path) -> str:
    """Return the stem of the path as the test case ID.
    tests/boards/benchmark-4x4.in -> benchmark-4x4
    """
    return path.stem


def test_fixtures_discovered() -> None:
    """Guard against an empty parametrize silently passing the whole suite.

    If the glob matches nothing, pytest collects zero cases and reports green --
    the same class of bug as test.ps1's unconditional exit 0.
    """
    assert len(FIXTURES) == 7


@pytest.mark.parametrize("in_path", FIXTURES, ids=_case_id)
def test_fixture(in_path: Path) -> None:
    """Run the solver on a fixture and assert that the output is expected."""
    out_path = in_path.with_suffix(".out")
    assert out_path.exists(), f"missing expected output for {in_path.name}"

    expected = out_path.read_text(encoding="utf-8").split()
    actual = solve(BoardInfo.from_file(in_path))

    assert actual == expected
