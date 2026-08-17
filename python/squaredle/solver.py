"""Invoke the C++ solver binary and return the words found."""

import subprocess
from pathlib import Path

from squaredle.board import BoardInfo
from squaredle.config import get_config


class SolverError(RuntimeError):
    """The solver binary failed or could not be run."""


def solve(board: BoardInfo, solver_path: Path | None = None) -> list[str]:
    """Run the solver on a board and return the words it found sorted.

    The binary sorts its own output, so the returned order is the binary's
    """
    binary = solver_path or get_config().SOLVER_PATH
    if not binary.exists():
        raise SolverError(f"Solver binary not found at {binary}")

    # The binary accepts letters and board_size as cli arguments; output
    # is written to stdout, one word per line, sorted.
    result = subprocess.run(
        [str(binary), board.letters, str(board.board_size)],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise SolverError(
            f"Solver binary failed with exit code {result.returncode}: "
            f"{result.stderr.strip()}"
        )

    # .split() and not .split("\n"): an empty solution must give [], not [""].
    return result.stdout.split()
