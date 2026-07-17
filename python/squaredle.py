import asyncio
import logging
from typing import Protocol

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

URL = "https://www.squaredle.app/"
URL_XP = "https://www.squaredle.app/?level=xp"


class SquaredleClient(Protocol):
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
        self._browser = await self._playwright.chromium.launch(headless=False)
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
            await asyncio.sleep(1)
        except Exception:
            logging.info("Closing popup...")
            popups = await self._page.query_selector_all(".popup")
            for popup in popups:
                if await popup.is_visible():
                    close = await popup.query_selector(".closeBtn")
                    if close:
                        await close.click()
                        await asyncio.sleep(0.5)

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
            await asyncio.sleep(0.5)

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


class SeleniumSquaredleClient:
    def __init__(self) -> None:
        service = Service()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self._browser = webdriver.Chrome(service=service, options=chrome_options)

        # Set a page load timeout
        self._browser.maximize_window()
        self._browser.set_page_load_timeout(20)

    async def get_board_html(self, url: str) -> str:
        try:
            logging.info("Fetching HTML...")
            self._browser.get(url)
            await asyncio.sleep(5)
            try:
                logging.info("Skipping tutorial...")
                self._browser.find_element(By.CLASS_NAME, "skipTutorial").click()
                self._browser.find_element(By.ID, "confirmAccept").click()
                await asyncio.sleep(1)
            except Exception:
                logging.info("Closing popup...")
                popups = self._browser.find_elements(By.CLASS_NAME, "popup")
                for popup in popups:
                    if popup.is_displayed():
                        close = popup.find_element(By.CLASS_NAME, "closeBtn")
                        ActionChains(self._browser).move_to_element(close).click(
                            close
                        ).perform()
                        await asyncio.sleep(0.5)

        except Exception as e:
            logging.info(f"{type(e).__name__}: {e}")
            await self.close()
            raise

        return self._browser.page_source

    async def input_words(self, words: list[str]) -> None:
        logging.info("Inputting found words...")
        try:
            actions = ActionChains(self._browser)

            popups = self._browser.find_elements(By.CLASS_NAME, "popup")
            for word in words:
                for _ in range(2):
                    actions.send_keys(word).perform()
                    actions.send_keys(Keys.ENTER).perform()

                    for popup in popups:
                        if popup.is_displayed():
                            try:
                                close = popup.find_element(By.CLASS_NAME, "closeBtn")
                                actions.move_to_element(close).click(close).perform()
                            except Exception as e:
                                logging.info(f"Error closing popup: {e}")

                            await asyncio.sleep(0.5)

                # Not critical, allow to fail silently
                await self._close_explainer(actions)

            await self._close_explainer(actions)

        except Exception as e:
            logging.info(f"Inputting Solution (error): {e}")

    async def _close_explainer(self, actions: ActionChains) -> None:
        for element_id in ["explainerPermaClose", "explainerClose"]:
            try:
                close = self._browser.find_element(By.ID, element_id)
                actions.move_to_element(close).click(close).perform()
                return
            except ElementClickInterceptedException:
                logging.warning(f"Explainer close button '{element_id}' was blocked")
            except ElementNotInteractableException:
                continue

    async def get_results(self) -> str:
        try:
            actions = ActionChains(self._browser)

            share = self._browser.find_element(By.CLASS_NAME, "sh4reBtn")
            actions.move_to_element(share).click(share).perform()

            el = self._browser.find_element(By.ID, "shareContent")
            result = el.get_attribute("textContent")

            logging.info("Fetching Results (success)")

            return str(result)
        except Exception as e:
            logging.info(f"Fetching Results (error): {e}")

        return ""

    async def close(self) -> None:
        self._browser.quit()
