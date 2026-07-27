import logging
from pathlib import Path

# refactor this to use pydantic

logging.basicConfig(level=logging.INFO)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOLVER_PATH = PROJECT_ROOT / "cpp" / "build" / "main.exe"

URL = "https://www.squaredle.app/"
URL_XP = "https://www.squaredle.app/?level=xp"
