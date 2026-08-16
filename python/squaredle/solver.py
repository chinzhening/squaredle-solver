"""Invoke the C++ solver binary and return the words found."""

import subprocess
import tempfile
from pathlib import Path

from squaredle.board_parser import BoardInfo
from squaredle.config import config


class SolverError(RuntimeError):
    """The solver binary failed or could not be run."""


def solve(board: BoardInfo, solver_path: Path | None = None) -> list[str]:
    """Run the solver on a board and return the words it found sorted.

    The binary sorts its own output, so the returned order is the binary's
    """
    binary = solver_path or config.SOLVER_PATH
    if not binary.exists():
        raise SolverError(f"Solver binary not found at {binary}")

    # The binary still reads its board from a file; stdout is supported, need
    # temp file for input.
    with tempfile.TemporaryDirectory() as tmp:
        board_file = Path(tmp) / "board_info.txt"
        board_file.write_text(
            f"{board.rating} {board.letters} {board.board_size}\n", encoding="utf-8"
        )
        result = subprocess.run(
            [str(binary), str(board_file)],
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
