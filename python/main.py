import asyncio
import logging
import os
import shutil
import subprocess
import tempfile

from board_parser import parse_board
from config import SOLVER_PATH, URL
from squaredle import PlaywrightSquaredleClient, SquaredleClient


async def main() -> None:
    # Playwright setup
    client: SquaredleClient = PlaywrightSquaredleClient()
    await client.start()

    temp_dir = tempfile.mkdtemp()

    try:
        board_info_path = os.path.join(temp_dir, "board_info.txt")

        board_html = await client.get_board_html(URL)
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

        await client.input_words(words)

        results = await client.get_results()

        print(f"Results:\n{results}\n")

    finally:
        shutil.rmtree(temp_dir)
        logging.info("Temporary files deleted.")

        # Close the browser window
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
