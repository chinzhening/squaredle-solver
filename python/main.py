import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# TODO: make this toggleable from a command line argument.
logging.basicConfig(level=logging.INFO)

# constants
URL = "https://www.squaredle.app/"
URL_XP = "htps://www.squaredle.app/?level=xp"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOLVER_PATH = PROJECT_ROOT / "cpp" / "build" / "main.exe"


def get_browser() -> webdriver.Chrome:
    service = Service()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser


def parse_star(star: Tag) -> float:
    classes = star.get("class")
    if classes is None:
        logging.warning("Star element does not have a 'class' attribute.")
    else:
        if "half" in classes:
            return 0.5

    style = star.get("style")
    if style is None:
        logging.warning("Star element does not have a 'style' attribute.")
    else:
        if "fill: none" in style:
            return 0

    return 1


def fetch_board_info(browser: webdriver.Chrome, path: str) -> None:
    try:
        logging.info("Fetching HTML...")
        browser.get(URL)
        time.sleep(5)
        try:
            logging.info("Skipping tutorial...")
            browser.find_element(By.CLASS_NAME, "skipTutorial").click()
            browser.find_element(By.ID, "confirmAccept").click()
            time.sleep(1)
        except Exception:
            logging.info("Closing popup...")
            popups = browser.find_elements(By.CLASS_NAME, "popup")
            for popup in popups:
                if popup.is_displayed():
                    close = popup.find_element(By.CLASS_NAME, "closeBtn")
                    ActionChains(browser).move_to_element(close).click(close).perform()
                    time.sleep(0.5)

    except Exception as e:
        logging.info(f"{type(e).__name__}: {e}")
        browser.quit()

    logging.info("Parsing source page...")
    soup = BeautifulSoup(browser.page_source, "html.parser")

    # TODO: wrap in try-except block
    difficulty_note = soup.find("div", class_="p difficultyNote")
    if not difficulty_note:
        raise ValueError("Difficulty note not found in the page source.")
    stars = difficulty_note.find_all("svg")
    rating = sum(parse_star(star) for star in stars)

    letters: list[str] = []
    board = soup.find("div", class_="board")
    if not board:
        raise ValueError("Board not found in the page source.")

    for t in board.find_all("div", class_="letter"):
        unnecessary_wrapper = t.find(class_="unnecessaryWrapper")
        if unnecessary_wrapper and unnecessary_wrapper.contents:
            letter = unnecessary_wrapper.contents[0].text
            if letter == " ":
                letter = "_"
            letters.append(letter)

    board_size = None
    match len(letters):
        case 9:
            board_size = 3
        case 16:
            board_size = 4
        case 25:
            board_size = 5
        case 36:
            board_size = 6
        case _:
            board_size = -1

    letter_str = "".join(letters)

    logging.info(f"Rating: {rating}")
    logging.info(f"Board: {letter_str}")
    logging.info(f"Boardsize: {board_size}")

    with open(path, "w") as f:
        f.write(f"{rating} {letter_str} {board_size}\n")


def input_solution(browser: webdriver.Chrome, solution_path: str) -> None:
    logging.info("Inputting found words...")

    with open(solution_path) as f:
        words = [line.strip() for line in f]

        try:
            actions = ActionChains(browser)

            popups = browser.find_elements(By.CLASS_NAME, "popup")
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
                try:
                    perma_close = browser.find_element(By.ID, "explainerPermaClose")
                    actions.move_to_element(perma_close).click(perma_close).perform()
                except Exception as e:
                    logging.info(f"Error closing explainer: {e}")

            try:
                explainer_close = browser.find_element(By.ID, "explainerClose")
                actions.move_to_element(explainer_close).click(
                    explainer_close
                ).perform()
            except Exception as e:
                logging.info(f"Error closing explainer: {e}")

        except Exception as e:
            logging.info(f"Inputting Solution (error): {e}")

        logging.info(f"Words found... {len(words)}")


def fetch_results(browser: webdriver.Chrome) -> str:
    try:
        actions = ActionChains(browser)

        share = browser.find_element(By.CLASS_NAME, "sh4reBtn")
        actions.move_to_element(share).click(share).perform()

        el = browser.find_element(By.ID, "shareContent")
        result = el.get_attribute("textContent")

        logging.info("Fetching Results (success)")

        return str(result)
    except Exception as e:
        logging.info(f"Fetching Results (error): {e}")

    return ""


if __name__ == "__main__":
    # Selenium setup
    browser = get_browser()
    browser.maximize_window()
    browser.set_page_load_timeout(20)

    temp_dir = tempfile.mkdtemp()

    try:
        board_info_path = os.path.join(temp_dir, "board_info.txt")
        fetch_board_info(browser, board_info_path)

        solution_path = os.path.join(temp_dir, "solution.txt")
        subprocess.run([str(SOLVER_PATH), board_info_path, solution_path], check=True)

        input_solution(browser, solution_path)

        results = fetch_results(browser)

        print(f"Results:\n{results}\n")

    finally:
        shutil.rmtree(temp_dir)
        logging.info("Temporary files deleted.")

        # Close the browser window
        browser.quit()
