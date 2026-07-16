import logging
import time
from typing import Protocol

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
    def get_board_html(self, url: str) -> str:
        """Navigate to URL, dismiss onboarding, return page HTML with board."""
        ...

    def input_words(self, words: list[str]) -> None:
        """Type each word + Enter into the board, dismissing any feedback
        popups and the explainer overlay as they appear."""
        ...

    def get_results(self) -> str:
        """Return the text of the results popup."""
        ...

    def close(self) -> None:
        """Release browser resources."""
        ...


class SeleniumSquaredleClient:
    def __init__(self) -> None:
        service = Service()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self._browser = webdriver.Chrome(service=service, options=chrome_options)

        # Set a page load timeout
        self._browser.maximize_window()
        self._browser.set_page_load_timeout(20)

    def get_board_html(self, url: str) -> str:
        try:
            logging.info("Fetching HTML...")
            self._browser.get(url)
            time.sleep(5)
            try:
                logging.info("Skipping tutorial...")
                self._browser.find_element(By.CLASS_NAME, "skipTutorial").click()
                self._browser.find_element(By.ID, "confirmAccept").click()
                time.sleep(1)
            except Exception:
                logging.info("Closing popup...")
                popups = self._browser.find_elements(By.CLASS_NAME, "popup")
                for popup in popups:
                    if popup.is_displayed():
                        close = popup.find_element(By.CLASS_NAME, "closeBtn")
                        ActionChains(self._browser).move_to_element(close).click(
                            close
                        ).perform()
                        time.sleep(0.5)

        except Exception as e:
            logging.info(f"{type(e).__name__}: {e}")
            self.close()
            raise

        return self._browser.page_source

    def input_words(self, words: list[str]) -> None:
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

                            time.sleep(0.5)

                # Not critical, allow to fail silently
                self._close_explainer(actions)

            self._close_explainer(actions)

        except Exception as e:
            logging.info(f"Inputting Solution (error): {e}")

    def _close_explainer(self, actions: ActionChains) -> None:
        for element_id in ["explainerPermaClose", "explainerClose"]:
            try:
                close = self._browser.find_element(By.ID, element_id)
                actions.move_to_element(close).click(close).perform()
                return
            except ElementClickInterceptedException:
                logging.warning(f"Explainer close button '{element_id}' was blocked")
            except ElementNotInteractableException:
                continue

    def get_results(self) -> str:
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

    def close(self) -> None:
        self._browser.quit()
