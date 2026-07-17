import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class BoardInfo:
    rating: float
    letters: str
    board_size: int


def parse_star(star: Tag) -> float:
    classes = star.get_attribute_list("class")
    styles = star.get_attribute_list("style")
    logging.debug(f"Star classes: {classes}, styles: {styles}")

    if classes and "half" in classes:
        return 0.5
    elif styles and "fill: none;" in styles:
        return 0

    return 1


def extract_rating(soup: BeautifulSoup) -> float:
    difficulty_note = soup.find("div", class_="p difficultyNote")
    if not difficulty_note:
        raise ValueError("Difficulty note not found in the page source.")
    stars = difficulty_note.find_all("svg")
    return sum(parse_star(star) for star in stars)


def extract_letters(board: Tag) -> str:
    letters: list[str] = []
    for t in board.find_all("div", class_="letter"):
        unnecessary_wrapper = t.find(class_="unnecessaryWrapper")
        if unnecessary_wrapper and unnecessary_wrapper.contents:
            letter = unnecessary_wrapper.contents[0].text
            if letter == " ":
                letter = "_"
            letters.append(letter)
    return "".join(letters)


def extract_board_size(count: int) -> int:
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


def parse_board(html: str) -> BoardInfo:
    soup = BeautifulSoup(html, "html.parser")

    board = soup.find("div", class_="board")
    if not board:
        raise ValueError("Board not found in the page source.")

    rating = extract_rating(soup)
    letters = extract_letters(board)

    try:
        board_size = extract_board_size(len(letters))
    except ValueError as e:
        logging.exception(e)
        raise

    logging.info(f"Rating: {rating}")
    logging.info(f"Board: {letters}")
    logging.info(f"Boardsize: {board_size}")

    return BoardInfo(rating=rating, letters=letters, board_size=board_size)
