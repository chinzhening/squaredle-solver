import asyncio
import logging

from squaredle.board_parser import parse_board
from squaredle.client import PlaywrightSquaredleClient, SquaredleClient
from squaredle.config import config
from squaredle.solver import solve
from squaredle.writers import SolveResult, build_writer


async def main() -> None:
    # Playwright setup
    client: SquaredleClient = PlaywrightSquaredleClient()
    await client.start()

    # TODO: use c++ bindings instead of temp directory
    # reduce file i/o from python and cpp and creates more options for interoperability
    # qn: is there a way to speedup trie generation. serializing the trie
    #     directly instead of re-generating it from scratch each time.

    try:
        board_html = await client.get_board_html(config.URL)
        board_info = parse_board(board_html)

        words = solve(board_info)
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
        # Close the browser window
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
