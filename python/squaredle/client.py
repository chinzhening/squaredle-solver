import logging
from typing import Protocol

from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError,
    async_playwright,
)

from squaredle.board import BoardInfo
from squaredle.results import SolutionState, WordOutcomes, classify, parse_solution

# Solution blobs for one board only. The mode is an argument rather than a
# field parsed back out later, and the two patterns are exact because
# "-solution" is a suffix of "-xp-solution" -- an endsWith would match both and
# reading the wrong board's blob marks every word rejected.
_READ_SOLUTIONS_JS = """
    (xp) => {
        const re = xp
            ? /^squaredle-\\d{4}\\/\\d{2}\\/\\d{2}-xp-solution$/
            : /^squaredle-\\d{4}\\/\\d{2}\\/\\d{2}-solution$/;
        return Object.keys(localStorage)
            .filter(k => re.test(k))
            .map(k => ({ key: k, value: localStorage.getItem(k) }));
    }
"""


def parse_board(html: str) -> BoardInfo:
    """Extract a board from a scraped page.

    Lives here rather than on BoardInfo so that board.py stays free of
    BeautifulSoup: solver.py imports BoardInfo, and the fixture tests should
    not need a HTML parser to run a C++ binary.
    """
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

    return BoardInfo(rating=rating, letters=letters, board_size=board_size)


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


class SquaredleClient(Protocol):
    async def start(self) -> None:
        """Start the client, e.g. launch browser."""
        ...

    async def get_board_html(self, url: str) -> str:
        """Navigate to URL, dismiss onboarding, return page HTML with board."""
        ...

    async def input_words(self, words: list[str]) -> WordOutcomes | None:
        """Type words into the board, dismissing any feedback popups and the
        explainer overlay as they appear, and report what each word did."""
        ...

    async def get_results(self) -> str:
        """Return the text of the results popup."""
        ...

    async def close(self) -> None:
        """Release browser resources."""
        ...


class PlaywrightSquaredleClient:
    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()

        self._page.set_default_timeout(5000)
        self._page.set_default_navigation_timeout(20_000)

    async def get_board_html(self, url: str) -> str:
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")

        logging.info("Fetching HTML...")
        await self._page.goto(url, wait_until="networkidle")

        # Skip tutorial
        logging.info("Skipping tutorial...")
        try:
            await self._page.click(".skipTutorial")
            await self._page.click("#confirmAccept")
        except Exception:
            logging.info("Closing popup...")
            popups = await self._page.query_selector_all(".popup")
            for popup in popups:
                if await popup.is_visible():
                    close = await popup.query_selector(".closeBtn")
                    if close:
                        await close.click()

        await self._page.wait_for_selector(".board")
        return await self._page.content()

    async def input_words(self, words: list[str]) -> WordOutcomes | None:
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")

        logging.info("Inputting found words...")
        for word in words:
            await self._page.type("body", word)
            await self._page.keyboard.press("Enter")

            await self._close_popups()
            await self._close_explainer()

        await self._close_explainer()

        # After every submission, so every write has landed: this is the only
        # read, and needs no baseline.
        state = await self._read_solution_state()
        if state is None:
            logging.warning("No solution state readable; outcomes not measured")
            return None

        outcomes = classify(words, state)
        logging.info(
            f"Submitted {len(words)}: {len(outcomes.accepted)} accepted, "
            f"{len(outcomes.bonus)} bonus, {len(outcomes.rejected)} rejected"
        )
        return outcomes

    async def _read_solution_state(self) -> SolutionState | None:
        """Squaredle's record of the board being played, snapshotted from localStorage.

        Requires exactly one stored solution for the current mode.
        """
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")

        # The mode comes from the URL navigated to, so the client needs no
        # config to know which board it is on.
        is_xp = "level=xp" in self._page.url

        try:
            entries = await self._page.evaluate(_READ_SOLUTIONS_JS, is_xp)
        except Exception as e:
            logging.warning(f"Could not read localStorage: {e}")
            return None

        states = [
            state
            for entry in entries
            if (state := parse_solution(entry["key"], entry["value"])) is not None
        ]

        # A persistent profile can hold several days for the same mode, and
        # reading the wrong one marks every word rejected -- so refuse rather
        # than pick.
        if len(states) != 1:
            logging.warning(
                f"Expected one stored {'xp' if is_xp else 'normal'} solution, "
                f"found {len(states)}"
            )
            return None

        return states[0]

    async def _close_popups(self) -> None:
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")
        for popup in await self._page.query_selector_all(".popup"):
            if await popup.is_visible():
                close = await popup.query_selector(".closeBtn")
                if close:
                    await close.click()

    async def _close_explainer(self) -> None:
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")

        for element_id in ["explainerPermaClose", "explainerClose"]:
            try:
                element = await self._page.query_selector(f"#{element_id}")
                if element and await element.is_visible():
                    await self._page.click(f"#{element_id}")
                    return
            except Exception as e:
                logging.error(f"Error closing explainer: {e}")
                continue

    async def get_results(self) -> str:
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")

        try:
            await self._page.click(".sh4reBtn")

            share = self._page.locator("#shareContent")
            initial = await share.inner_text()

            await self._page.wait_for_function(
                """
                ({ initial }) => {
                    const el = document.querySelector("#shareContent");
                    return el && el.innerText !== initial;
                }
                """,
                arg={"initial": initial},
                timeout=10000,
            )

            result = await share.inner_text()

            logging.info("Fetching Results (success)")
            return result.strip()

        except TimeoutError as e:
            logging.warning(f"Fetching Results (timeout): {e}")

            share = self._page.locator("#shareContent")
            result = await share.inner_text()
            return result.strip()

        except Exception as e:
            logging.info(f"Fetching Results (error): {e}")

        return ""

    async def close(self) -> None:
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
