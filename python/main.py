import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from board_parser import parse_board
from squaredle import URL, SeleniumSquaredleClient

# TODO: make this toggleable from a command line argument.
logging.basicConfig(level=logging.INFO)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOLVER_PATH = PROJECT_ROOT / "cpp" / "build" / "main.exe"


if __name__ == "__main__":
    # Selenium setup
    client = SeleniumSquaredleClient()

    temp_dir = tempfile.mkdtemp()

    try:
        board_info_path = os.path.join(temp_dir, "board_info.txt")

        board_html = client.get_board_html(URL)
        board_info = parse_board(board_html)

        with open(board_info_path, "w") as f:
            rating = board_info.rating
            letters = board_info.letters
            board_size = board_info.board_size
            f.write(f"{rating} {letters} {board_size}\n")

        solution_path = os.path.join(temp_dir, "solution.txt")
        subprocess.run([str(SOLVER_PATH), board_info_path, solution_path], check=True)

        with open(solution_path) as f:
            words = [line.strip() for line in f]
            logging.info(f"Words found: {len(words)}")

        client.input_words(words)

        results = client.get_results()

        print(f"Results:\n{results}\n")

    finally:
        shutil.rmtree(temp_dir)
        logging.info("Temporary files deleted.")

        # Close the browser window
        client.close()
