import asyncio
import logging
import os
import shutil
import subprocess
import tempfile

from board_parser import parse_board
from config import config
from squaredle import PlaywrightSquaredleClient, SquaredleClient
from writers import SolveResult, build_writer


async def main() -> None:
    # Playwright setup
    client: SquaredleClient = PlaywrightSquaredleClient()
    await client.start()

    # TODO: use c++ bindings instead of temp directory
    # reduce file i/o from python and cpp and creates more options for interoperability
    # qn: is there a way to speedup trie generation. serializing the trie
    #     directly instead of re-generating it from scratch each time.
    temp_dir = tempfile.mkdtemp()

    try:
        board_info_path = os.path.join(temp_dir, "board_info.txt")

        board_html = await client.get_board_html(config.URL)
        board_info = parse_board(board_html)

        with open(board_info_path, "w") as f:
            rating = board_info.rating
            letters = board_info.letters
            board_size = board_info.board_size
            f.write(f"{rating} {letters} {board_size}\n")

        solution_path = os.path.join(temp_dir, "solution.txt")
        subprocess.run(
            [str(config.SOLVER_PATH), board_info_path, solution_path], check=True
        )

        with open(solution_path) as f:
            words = [line.strip() for line in f]
            logging.info(f"Words found: {len(words)}")

        await client.input_words(words)

        share_text = await client.get_results()

        # TODO: telegram (bot) writer -> possible but probably won't deploy

        # set up run daily job on github actions
        async with build_writer(config) as writer:
            await writer.write(
                SolveResult(
                    url=config.URL,
                    board=board_info,
                    words=words,
                    share_text=share_text,
                )
            )

    finally:
        shutil.rmtree(temp_dir)
        logging.info("Temporary files deleted.")

        # Close the browser window
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
