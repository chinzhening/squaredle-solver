# squaredle-solver

Solves [Squaredle](https://www.squaredle.app/). Written in C++ for performance.  
It scrapes the board from the website, preprocesses it, then solves the board using a Trie-based backtracking algorithm.

## requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (manages the virtual environment and Python dependencies)
- g++ with C++17 support (MinGW on Windows)
- CMake 3.16+: https://cmake.org/download/

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

5. **Run the tests.** Requires step 4 to have been run first. The fixture
   tests drive the binary through `squaredle.solver.solve`, so they run
   anywhere Python does:

   ```powershell
   cd python
   uv run pytest -v
   ```

## usage

Run the Python script:

```powershell
cd python
uv run python -m squaredle
```

## benchmarking

Timings come from [Google Benchmark](https://github.com/google/benchmark), pinned to
`v1.9.5` and fetched automatically on first use. It is gated behind
`-DBUILD_BENCHMARKS=ON`, so a normal `build.ps1` needs no network and pulls in no
dependencies.

```powershell
# Build and run the whole suite
.\cpp\scripts\benchmark.ps1

# Any Google Benchmark flag is forwarded to the binary
.\cpp\scripts\benchmark.ps1 --benchmark_filter=BM_SolveBoard

# Run directly once built, skipping the CMake reconfigure
.\cpp\build\bench.exe --benchmark_filter="BM_LoadWordTrie|BM_EndToEnd"
.\cpp\build\bench.exe --benchmark_list_tests=true
```

Registered benchmarks: `BM_LoadWordTrie`, `BM_SolveBoard/{3x3,4x4,5x5}` and
`BM_EndToEnd/4x4`. Boards are transcribed from `tests/boards`.

**Before trusting a number**, check the run-to-run spread — this project is
developed on a hybrid laptop CPU where background load and core migration move
results by tens of percent. Run this twice and compare the `_cv` rows:

```powershell
.\cpp\build\bench.exe --benchmark_repetitions=10 --benchmark_report_aggregates_only=true
```

Once the machine is quiet, capture a run for the record:

```powershell
.\cpp\build\bench.exe --benchmark_repetitions=10 `
    --benchmark_report_aggregates_only=true `
    --benchmark_format=json > cpp\bench\results\baseline-<date>.json
```

See [`cpp/bench/RESULTS.md`](cpp/bench/RESULTS.md) for recorded results, the
environment they were taken in, and the stability gate.

### diagnostic counters

DFS recursion and backtrack counts are a separate runtime flag, deliberately kept
out of the timed path — never benchmark a run with it on:

```powershell
.\cpp\build\main.exe tests\boards\benchmark-4x4.in --stats
```

## project structure

```
.
├── LICENSE
├── README.md
├── cpp
│   ├── CMakeLists.txt
│   ├── bench
│   │   ├── bench_main.cpp
│   │   ├── RESULTS.md
│   │   └── results
│   ├── data
│   ├── src
│   └── scripts
│       ├── build.ps1
│       └── benchmark.ps1
├── python
│   ├── squaredle
│   │   ├── __main__.py
│   │   ├── board.py
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── solver.py
│   │   └── writers.py
│   ├── tests
│   │   └── test_solver.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env.example
└── tests
    └── cpp
        └── xp
```
