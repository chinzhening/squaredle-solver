import logging
from typing import Protocol

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)


class SquaredleClient(Protocol):
    async def start(self) -> None:
        """Start the client, e.g. launch browser."""
        ...

    async def get_board_html(self, url: str) -> str:
        """Navigate to URL, dismiss onboarding, return page HTML with board."""
        ...

    async def input_words(self, words: list[str]) -> None:
        """Type each word + Enter into the board, dismissing any feedback
        popups and the explainer overlay as they appear."""
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

    async def input_words(self, words: list[str]) -> None:
        if self._page is None:
            raise RuntimeError("Playwright client not started. Call start() first.")

        popups = await self._page.query_selector_all(".popup")

        logging.info("Inputting found words...")
        for word in words:
            await self._page.type("body", word)
            await self._page.keyboard.press("Enter")

            for popup in popups:
                if await popup.is_visible():
                    close = await popup.query_selector(".closeBtn")
                    if close:
                        await close.click()

            # Close explainers if they appear
            await self._close_explainer()

        await self._close_explainer()

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
            result_element = await self._page.query_selector("#shareContent")
            if result_element:
                result = await result_element.text_content()
                logging.info("Fetching Results (success)")
                return result or ""
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
