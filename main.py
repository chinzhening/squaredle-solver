import logging
import os
import shutil
import subprocess
import tempfile
import time

from bs4 import BeautifulSoup
from bs4.element import Tag

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logging.basicConfig(
    level=logging.INFO
)

# constants
URL = "https://www.squaredle.app/"


def get_browser() -> webdriver.Chrome:
    service = Service()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser

def parse_star(star : Tag) -> float:
    if "halfStar" in star.get("class", []):
        return 0.5
    elif "fill: none" in star.get("style", ""):
        return 0
    else:
        return 1

def fetch_board_info(browser : webdriver.Chrome, path : str) -> None:
    try:
        logging.info("Fetching HTML...")
        browser.get(URL)
        time.sleep(5)
        try:
            logging.info("Skipping tutorial...")
            browser.find_element(By.CLASS_NAME, "skipTutorial").click()
            browser.find_element(By.ID, "confirmAccept").click()
            time.sleep()
        except:
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

    rating = sum(parse_star(star) for star in soup.find("div", class_="p difficultyNote").find_all("svg"))
    letters = "".join(t.find(class_="unnecessaryWrapper").contents[0] for t in soup.find("div", class_="board").find_all("div", class_="letter"))

    logging.info(f"Rating: {rating}")
    logging.info(f"Board: {letters}")

    with open(path, "w") as f:
        f.write(f"{rating} {letters}\n")

def input_solution(browser : webdriver.Chrome, solution_path : str) -> None:
    
    logging.info("Inputting found words...")
    
    with open(solution_path, 'r') as f:
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
                            except:
                                pass
                            time.sleep(0.5)

                # Not critical, allow to fail silently
                try:
                    explainer_perma_close = browser.find_element(By.ID, "explainerPermaClose")
                    actions.move_to_element(explainer_perma_close).click(explainer_perma_close).perform()
                except:
                    pass

            try:
                explainer_close = browser.find_element(By.ID, "explainerClose")
                actions.move_to_element(explainer_close).click(explainer_close).perform()
            except:
                pass

        except Exception as e:
            logging.info(f"Inputting Error: {e}")
        
        logging.info(f"Words found... {len(words)}")

def fetch_results(browser : webdriver.Chrome) -> str:
    actions = ActionChains(browser)
    
    share = browser.find_element(By.CLASS_NAME, "sh4reBtn")
    actions.move_to_element(share).click(share).perform()

    result = browser.find_element(By.ID, "shareContent").get_attribute("textContent")
    logging.info(f"\n{result}")

if __name__ == "__main__":
    # Selenium setup
    browser = get_browser()
    browser.maximize_window()
    browser.set_page_load_timeout(20)
    
    data_dir = "data"
    temp_dir = tempfile.mkdtemp()

    try:
        word_list_path = os.path.join(data_dir, "NWL2023.txt")

        board_info_path = os.path.join(temp_dir, "board_info.txt")
        fetch_board_info(browser, board_info_path)

        solution_path = os.path.join(temp_dir, "solution.txt")
        subprocess.run([
            "solver.exe",
            board_info_path,
            word_list_path,
            solution_path
        ], check=True)


        input_solution(browser, solution_path)
        
        fetch_results(browser)

    finally:
        shutil.rmtree(temp_dir)
        logging.info("Temporary files deleted.")

        # Close the browser window
        browser.quit()