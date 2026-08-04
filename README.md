# squaredle-solver

Solves [Squaredle](https://www.squaredle.app/). Written in C++ for performance.  
It scrapes the board from the website, preprocesses it, then solves the board using a Trie-based backtracking algorithm.

## requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (manages the virtual environment and Python dependencies)
- g++ with C++17 support (MinGW on Windows)
- CMake 3.10+: https://cmake.org/download/

Python dependencies (Playwright, BeautifulSoup4, pydantic-settings, pymongo) are declared in `python/pyproject.toml` and installed by `uv sync`.

## installation

1. **Clone this repository:**

   ```powershell
   git clone https://github.com/chinzhening/squaredle-solver.git
   cd squaredle-solver
   ```

2. **Install the Python dependencies.** `uv sync` creates `python/.venv` and installs
   everything from the lockfile, so there is no virtual environment to set up by hand.

   ```powershell
   cd python
   uv sync
   uv run playwright install
   ```

3. **Configure (optional).** Every setting has a working default, so a fresh clone runs
   without any configuration. To solve the XP board or write results to MongoDB, copy the
   example file and edit it:

   ```powershell
   copy .env.example .env
   ```

4. **Build the C++ executable.** On Windows (PowerShell):

   ```powershell
   .\cpp\scripts\build.ps1
   ```

   This writes `cpp/build/main.exe`, which is where `SOLVER_PATH` points by default.

5. **Run the tests.** Requires step 4 to have been run first. On Windows (PowerShell):

   ```powershell
   .\cpp\scripts\test.ps1
   ```

   `benchmark.ps1` rebuilds with `-DENABLE_BENCHMARKING=ON` and runs the timing pass:

   ```powershell
   .\cpp\scripts\benchmark.ps1
   ```

## usage

Run the Python script:

```powershell
cd python
uv run main.py
```

## project structure

```
.
├── LICENSE
├── README.md
├── cpp
│   ├── CMakeLists.txt
│   ├── benchmark
│   ├── data
│   ├── src
│   └── scripts
│       ├── build.ps1
│       ├── test.ps1
│       └── benchmark.ps1
├── python
│   ├── main.py
│   ├── board_parser.py
│   ├── config.py
│   ├── squaredle.py
│   ├── writers.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env.example
└── tests
    └── cpp
        └── xp
```
