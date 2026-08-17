import sys
from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parent  # python/squaredle
PROJECT_ROOT = PACKAGE_ROOT.parent.parent  # repo root

# Derived here so neither workflow needs a SOLVER_PATH override.
SOLVER_NAME = "main.exe" if sys.platform == "win32" else "main"


class Config(BaseSettings):
    """Runtime settings, sourced from python/.env - see .env.example.

    Real environment variables win over .env entries, so CI can inject secrets
    without writing a file. Every field keeps a working default, so a fresh
    clone runs without a .env at all.
    """

    model_config = SettingsConfigDict(
        # Absolute, so the settings load the same way regardless of the
        # working directory the solver is invoked from.
        env_file=PACKAGE_ROOT.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Puzzle source
    URL_NORMAL: str = "https://squaredle.app/"
    URL_XP: str = "https://squaredle.app/?level=xp"
    USE_XP: bool = False

    # Solver binary built from cpp/
    SOLVER_PATH: Path = PROJECT_ROOT / "cpp" / "build" / SOLVER_NAME

    # Result writers — MongoDB is opt-in since it needs a URI
    ENABLE_STDOUT_WRITER: bool = True
    ENABLE_MONGO_WRITER: bool = False
    MONGO_URI: SecretStr = SecretStr("")
    MONGO_DATABASE: str = "squaredle"
    MONGO_COLLECTION: str = "results"

    @property
    def URL(self) -> str:
        return self.URL_XP if self.USE_XP else self.URL_NORMAL

    @model_validator(mode="after")
    def _require_mongo_uri_when_enabled(self) -> Self:
        """Fail at startup rather than after a full solve."""
        if self.ENABLE_MONGO_WRITER and not self.MONGO_URI.get_secret_value():
            raise ValueError("ENABLE_MONGO_WRITER is true but MONGO_URI is not set.")
        return self


@lru_cache(maxsize=1)
def get_config() -> Config:
    """The process-wide settings, built on first use.

    Lazy, not a module-level Config(): that validated the environment as an
    import side effect, so a bad MONGO_URI failed an import rather than a run.
    """
    return Config()
