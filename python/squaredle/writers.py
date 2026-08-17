import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from types import TracebackType
from typing import Any, Protocol, Self

from pymongo import AsyncMongoClient

from squaredle.board import BoardInfo
from squaredle.config import Config
from squaredle.share import puzzle_date_from_run

# The shape as_document() produces. Not in config.py: an operator has no
# business setting it, and keeping it beside the method that defines the shape
# means both change in the same diff. Migrations import this.
#
# 1: adds puzzle_date and puzzle_date_source. An unversioned document predates
#    both, and predates any measurement of rejected words.
SCHEMA_VERSION = 1


def as_bson_date(day: date | None) -> datetime | None:
    """Widen a calendar day to the datetime BSON stores.

    BSON has no date type, so a bare date cannot be encoded. Midnight UTC is
    the canonical widening and the time component means nothing; everything
    writes it identically, so exact-match lookups are reliable.
    """
    if day is None:
        return None
    return datetime(day.year, day.month, day.day, tzinfo=UTC)


@dataclass
class SolveResult:
    """Everything worth publishing about a single solved board."""

    url: str
    board: BoardInfo
    words: list[str]
    share_text: str
    puzzle_date: date | None = None
    solved_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Derive puzzle_date so no caller can forget to.

        Both inputs the parse needs are already fields here. An explicit value
        still wins, which is what lets a migration supply its own.
        """
        if self.puzzle_date is None:
            self.puzzle_date = puzzle_date_from_run(self.share_text, self.solved_at)

    def as_document(self) -> dict[str, Any]:
        """Flatten into a document suitable for storage."""
        return {
            "url": self.url,
            "rating": self.board.rating,
            "letters": self.board.letters,
            "board_size": self.board.board_size,
            "words": self.words,
            "word_count": len(self.words),
            "share_text": self.share_text,
            "puzzle_date": as_bson_date(self.puzzle_date),
            "solved_at": self.solved_at,
            "schema_version": SCHEMA_VERSION,
        }

    def identity(self) -> dict[str, Any]:
        """The upsert filter identifying this document's puzzle.

        identity: (url, puzzle_date)

        Letters is the fallback for an unparsed date, so a failed parse still
        replaces its own earlier attempt. That case is deliberately outside the
        unique index - there is no identity to enforce without a date.
        """
        if self.puzzle_date is not None:
            return {"url": self.url, "puzzle_date": as_bson_date(self.puzzle_date)}
        return {"url": self.url, "letters": self.board.letters}


class ResultWriter(Protocol):
    async def write(self, result: SolveResult) -> None:
        """Publish a result to this writer's destination."""
        ...

    async def close(self) -> None:
        """Release any resources held by the writer."""
        ...


class StdoutWriter:
    """Prints a human-readable summary to stdout (captured by CI logs)."""

    async def write(self, result: SolveResult) -> None:
        board = result.board
        print(
            f"Solved {result.url}\n"
            f"  Rating:     {board.rating}\n"
            f"  Board:      {board.letters} ({board.board_size}x{board.board_size})\n"
            f"  Words found: {len(result.words)}\n"
            f"  Solved at:  {result.solved_at.isoformat()}\n"
            f"\n{result.share_text}\n"
        )

    async def close(self) -> None:
        return None


class MongoWriter:
    """Stores the full result in MongoDB, upserted per puzzle.

    A puzzle is identified by SolveResult.identity(), so re-running the solver
    on the same puzzle refreshes its document instead of duplicating it.
    """

    def __init__(self, uri: str, database: str, collection: str) -> None:
        self._client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(uri)
        self._collection = self._client[database][collection]

    async def write(self, result: SolveResult) -> None:
        document = result.as_document()
        outcome = await self._collection.replace_one(
            result.identity(),
            document,
            upsert=True,
        )
        action = "inserted" if outcome.upserted_id else "updated"
        logging.info(
            f"MongoDB: {action} result for puzzle {result.puzzle_date} "
            f"(board {document['letters']})"
        )

    async def close(self) -> None:
        await self._client.close()


class CompositeWriter:
    """Fans a result out to every configured writer.

    A failing destination is logged and skipped so it cannot take the others
    down with it.
    """

    def __init__(self, writers: list[ResultWriter]) -> None:
        self._writers = writers

    async def write(self, result: SolveResult) -> None:
        outcomes = await asyncio.gather(
            *(writer.write(result) for writer in self._writers),
            return_exceptions=True,
        )
        for writer, outcome in zip(self._writers, outcomes, strict=True):
            if isinstance(outcome, BaseException):
                name = type(writer).__name__
                logging.error(f"{name} failed to write result: {outcome}")

    async def close(self) -> None:
        outcomes = await asyncio.gather(
            *(writer.close() for writer in self._writers),
            return_exceptions=True,
        )
        for writer, outcome in zip(self._writers, outcomes, strict=True):
            if isinstance(outcome, BaseException):
                name = type(writer).__name__
                logging.error(f"{name} failed to close: {outcome}")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()


def build_writer(config: Config) -> CompositeWriter:
    """Assemble the writers enabled in configuration."""
    writers: list[ResultWriter] = []

    if config.ENABLE_STDOUT_WRITER:
        writers.append(StdoutWriter())

    if config.ENABLE_MONGO_WRITER:
        # Config validates that the URI is present whenever the writer is on.
        writers.append(
            MongoWriter(
                uri=config.MONGO_URI.get_secret_value(),
                database=config.MONGO_DATABASE,
                collection=config.MONGO_COLLECTION,
            )
        )

    if not writers:
        logging.warning("No writers enabled; results will be discarded.")

    return CompositeWriter(writers)
