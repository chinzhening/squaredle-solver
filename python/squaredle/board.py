import logging
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class BoardInfo:
    rating: float
    letters: str
    board_size: int

    @classmethod
    def try_from_file(cls, path: Path) -> "BoardInfo":
        """Read a board from a file."""
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

    @classmethod
    def try_from_html(cls, html: str) -> "BoardInfo":
        """Read a board from HTML."""
        soup = BeautifulSoup(html, "html.parser")

        board = soup.find("div", class_="board")
        if not board:
            raise ValueError("Board not found in the page source.")

        rating = _extract_rating(soup)
        letters = _extract_letters(board)

        try:
            board_size = _extract_board_size(len(letters))
        except ValueError as e:
            logging.exception(e)
            raise

        logging.info(f"Rating: {rating}")
        logging.info(f"Board: {letters}")
        logging.info(f"Boardsize: {board_size}")

        return cls(rating=rating, letters=letters, board_size=board_size)

    def write_to(self, path: Path) -> None:
        """Write a board to a file."""
        # write_text returns the character count and raises on failure, so
        # there is no return value worth branching on.
        path.write_text(
            f"{self.rating} {self.letters} {self.board_size}\n", encoding="utf-8"
        )
        logging.debug(f"Wrote board to {path}")


def _parse_star(star: Tag) -> float:
    classes = star.get_attribute_list("class")
    styles = star.get_attribute_list("style")
    logging.debug(f"Star classes: {classes}, styles: {styles}")

    if classes and "halfStar" in classes:
        return 0.5
    elif styles and "fill: none;" in styles:
        return 0

    return 1


def _extract_rating(soup: BeautifulSoup) -> float:
    difficulty_note = soup.find("div", class_="p difficultyNote")
    if not difficulty_note:
        raise ValueError("Difficulty note not found in the page source.")
    stars = difficulty_note.find_all("svg")
    return sum(_parse_star(star) for star in stars)


def _extract_letters(board: Tag) -> str:
    letters: list[str] = []
    for t in board.find_all("div", class_="letter"):
        unnecessary_wrapper = t.find(class_="unnecessaryWrapper")
        if unnecessary_wrapper and unnecessary_wrapper.contents:
            letter = unnecessary_wrapper.contents[0].text
            if letter == " ":
                letter = "_"
            letters.append(letter)
    return "".join(letters)


def _extract_board_size(count: int) -> int:
    match count:
        case 9:
            return 3
        case 16:
            return 4
        case 25:
            return 5
        case 36:
            return 6
        case _:
            raise ValueError(f"Unable to determine board size: {count} letters found.")
