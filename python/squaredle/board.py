from dataclasses import dataclass
from pathlib import Path
from typing import Self


@dataclass
class BoardInfo:
    """A puzzle board: its difficulty rating, letters, and side length.

    Deliberately free of scraping concerns -- HTML parsing lives in client.py,
    so importing a board does not drag BeautifulSoup in behind it.
    """

    rating: float
    letters: str
    board_size: int

    @classmethod
    def from_file(cls, path: Path) -> Self:
        """Read a board from the `<rating> <letters> <size>` fixture format."""
        if not path.exists():
            raise FileNotFoundError(f"Board file not found: {path}")

        # Conversions belong inside the try: a bad rating is just as much a
        # format error as the wrong field count, and should read the same way.
        try:
            rating, letters, board_size = path.read_text(encoding="utf-8").split()
            return cls(
                rating=float(rating), letters=letters, board_size=int(board_size)
            )
        except ValueError as e:
            raise ValueError(f"Invalid board file format: {path}") from e
