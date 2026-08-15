# Benchmark results

Tracks solver performance across the arena-trie (WS1) and CSR-serialization
(WS2) work. Every number here must be reproducible from a committed JSON run
in [`results/`](results/) — a figure quoted without its JSON does not count.

Capture both baselines with one command:

```powershell
.\cpp\scripts\benchmark.ps1 -Baseline
```

## Environment

| | |
|---|---|
| CPU | 12th Gen Intel Core i7-1255U, 10 cores / 12 threads (2 P + 8 E) |
| Caches | L1d 48 KiB x6, L1i 32 KiB x6, L2 1280 KiB x6, L3 12288 KiB |
| RAM | 16 GB |
| OS | Windows 11 Home 10.0.26200 |
| Compiler | g++ 16.1.0 (MinGW-w64, x86_64-posix-seh) |
| Build | CMake 4.0.2, MinGW Makefiles, `-DCMAKE_BUILD_TYPE=Release` |
| Flags | `-O3 -DNDEBUG -std=gnu++17` |
| Google Benchmark | v1.9.5, pinned via FetchContent |
| Machine idle | 2026-08-10 capture: yes |

This is a hybrid U-series laptop part. Thread migration between P- and E-cores
and sustained-load throttling are real variance sources; ~2% cv is the
practical floor for the microbenchmarks and ~10% for cold-start.

## Two regimes, and why both are recorded

The two disagree by ~35%, and each answers a different question.

| | What it measures | Use it for |
|---|---|---|
| **Steady-state** | In-process loop, allocator warmed by prior iterations | A/B comparison between workstreams — low variance |
| **Cold-start** | Fresh process per run | The headline — this is what actually ships |

The solver builds its trie once and exits, so **it never reaches the allocator
steady state the benchmark loop enjoys**. 436k individual `new TrieNode` calls
in a fresh process pay full `VirtualAlloc`, soft page-fault and page-zeroing
cost; in a loop the allocator recycles already-committed pages after ~60
build/destroy cycles. Quote cold-start when describing real behaviour.

This matters for attributing WS1. The arena replaces those 436k allocations
with one — precisely the cost the steady-state loop has already hidden.
Measured only in steady state, WS1 will look weaker than it is in production.

## Baseline — WS0, 2026-08-10

Steady-state: [`results/baseline-2026-08-10.json`](results/baseline-2026-08-10.json)
(10 repetitions, 8s warmup per benchmark).

| Benchmark | Mean | Median | Stddev | cv |
|---|---|---|---|---|
| `BM_LoadWordTrie` | 98.08 ms | 98.57 ms | 5.59 ms | 5.70% |
| `BM_SolveBoard/3x3` | 8.56 µs | 8.55 µs | 0.15 µs | 1.77% |
| `BM_SolveBoard/4x4` | 39.20 µs | 38.94 µs | 0.69 µs | 1.75% |
| `BM_SolveBoard/5x5` | 15.77 µs | 15.81 µs | 0.29 µs | 1.86% |
| `BM_EndToEnd/4x4` | 90.79 ms | 89.48 ms | 3.13 ms | 3.45% |

Cold-start: [`results/coldstart-2026-08-10.json`](results/coldstart-2026-08-10.json)
(20 fresh `main.exe` invocations on `tests/cpp/5.in`).

| Metric | Value |
|---|---|
| Mean | 142.12 ms |
| Median | 135.54 ms |
| Stddev | 15.01 ms (cv 10.56%) |
| Min / Max | 124.66 / 175.32 ms |

### Reading these numbers

**The search is ~0.03% of runtime.** `BM_SolveBoard/4x4` is 39 µs against a
135 ms cold-start median. Everything else is building a 436k-node trie from
2 MB of text, on every single invocation. That is the target for WS1 and WS2.

**`BM_LoadWordTrie` and `BM_EndToEnd` are not independently meaningful.**
They differ by exactly one solve — 39 µs against ~4 ms of noise, a ratio of
200:1 — so they measure the same quantity and the sign of their difference is
noise. Run in isolation with identical warmup they converge: 94.1 ms and
93.9 ms respectively. Do not read the in-suite gap (98.1 vs 90.8) as a real
effect; it is position bias, and it is why the warmup below is mandatory.

**`BM_SolveBoard` is the trustworthy microbenchmark.** It builds the trie
outside the timed loop, so it is immune to the allocator effects above and
holds cv under 2%. `BM_SolveBoard/4x4` also independently reproduces the
39,776 ns measured by the old ad-hoc harness — two unrelated timing paths
agreeing is the best evidence the harness is sound.

**Board size does not order the solve time.** 5x5 (15.8 µs) is faster than
4x4 (39.2 µs) because the 5x5 fixture is a blanked express board: 4 of its 25
cells are `_`, which terminate the DFS immediately and fragment the grid.

## Load-trie split — 2026-08-15

`load_word_trie` now splits into `read_words_from_files` (file I/O + line
parsing) and `build_trie_from_words` (trie insertion), each independently
benchmarked as `BM_ReadWordLists` and `BM_InsertWordsIntoTrie`.
`BM_LoadWordTrie` is unchanged and still measures the combined cost.

Steady-state: [`results/baseline-2026-08-15.json`](results/baseline-2026-08-15.json)
(10 repetitions, 8s warmup per benchmark).

| Benchmark | Mean | Median | Stddev | cv |
|---|---|---|---|---|
| `BM_LoadWordTrie` | 108.44 ms | 106.61 ms | 11.39 ms | 10.50% |
| `BM_ReadWordLists` | 7.58 ms | 7.32 ms | 0.90 ms | 11.84% |
| `BM_InsertWordsIntoTrie` | 85.74 ms | 85.52 ms | 0.84 ms | 0.98% |
| `BM_SolveBoard/3x3` | 8.55 µs | 8.57 µs | 0.14 µs | 1.69% |
| `BM_SolveBoard/4x4` | 41.85 µs | 41.77 µs | 0.64 µs | 1.52% |
| `BM_SolveBoard/5x5` | 18.03 µs | 18.11 µs | 0.61 µs | 3.38% |
| `BM_EndToEnd/4x4` | 95.83 ms | 95.50 ms | 1.36 ms | 1.42% |

Cold-start: [`results/coldstart-2026-08-15.json`](results/coldstart-2026-08-15.json)
(20 fresh `main.exe` invocations on `tests/cpp/5.in`).

| Metric | Value |
|---|---|
| Mean | 156.33 ms |
| Median | 143.97 ms |
| Stddev | 28.60 ms (cv 18.29%) |
| Min / Max | 137.54 / 252.34 ms |

**Insertion dominates load time.** ~85.7 ms of the load is trie insertion
against ~7.6 ms of file I/O and line parsing — an 11:1 split. This confirms
WS1 (arena trie) is targeting the right cost: the `new TrieNode` calls, not
the file read.

**`BM_LoadWordTrie`'s cv (10.5%) is higher than its 5.7% in the WS0
baseline**, and read + insert's means (7.58 + 85.74 = 93.3 ms) don't fully
sum to `BM_LoadWordTrie`'s 108.4 ms mean. Both are the same position-bias /
allocator-state effect documented below — two more benchmark families now run
ahead of `BM_LoadWordTrie` in-suite than in the WS0 capture. It is not a
discrepancy in the split itself.

**This cold-start capture is noisier than WS0's** (cv 18.29% vs the 10.56%
floor recorded there, including a 252 ms outlier on the first sample) — the
machine was not confirmed idle for this run. Treat it as indicative, not a
replacement headline figure.

## Measurement methodology

The 8s warmup in the capture is not optional, and it is the fix for a real
defect found while validating this harness.

Without it, a benchmark's result depended on how many trie build/destroy
cycles had already run in the same process. `BM_EndToEnd`, registered last,
measured 87 ms in-suite but 126 ms alone — a 44 ms swing from position alone,
larger than anything WS1 or WS2 is expected to change. Earlier still, before
`--benchmark_repetitions` was used at all, back-to-back runs on an unchanged
tree disagreed by 30-80%; that turned out to be background `esbuild` processes
plus a Balanced power plan, not the code.

Before capturing a baseline:

1. Quiet the machine — no builds, no dev servers, no browser.
2. Power plan to High Performance.
3. Run the suite twice; require cv under ~2% on `BM_SolveBoard` and stable
   medians elsewhere.

Report every figure as mean, median, stddev and cv. A bare mean is what made
the May "no visible improvement" question unanswerable.

## Comparing runs

Google Benchmark ships `compare.py`, which reports statistical significance
between two JSON captures. Not yet wired up — it needs `numpy` and `scipy`,
which are not installed. When picked up:

```powershell
uv run --with numpy --with scipy `
    cpp\.deps\googlebenchmark-src\tools\compare.py benchmarks `
    cpp\bench\results\baseline-2026-08-10.json `
    cpp\bench\results\<candidate>.json
```

The JSON in `results/` is the durable artifact; `compare.py` only reads it
after the fact, so deferring costs nothing.

## Running

```powershell
# Build and run the whole suite
.\cpp\scripts\benchmark.ps1

# Any Google Benchmark flag is forwarded to the binary
.\cpp\scripts\benchmark.ps1 --benchmark_filter=BM_SolveBoard

# Capture both baselines into results/
.\cpp\scripts\benchmark.ps1 -Baseline

# Run directly once built, skipping the CMake reconfigure
.\cpp\build\bench.exe --benchmark_list_tests=true
```

Diagnostic counters live behind a separate flag and must never be timed:

```powershell
.\cpp\build\main.exe tests\cpp\5.in --stats
```
