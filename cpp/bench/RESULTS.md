# Benchmark results

Tracks solver performance across the arena-trie (WS1) and CSR-serialization
(WS2) work. Every number here must be reproducible from a committed JSON run
in [`results/`](results/) — a figure quoted without its JSON does not count.

## Environment

| | |
|---|---|
| CPU | 12th Gen Intel Core i7-1255U, 10 cores / 12 threads |
| Caches | L1d 48 KiB x6, L1i 32 KiB x6, L2 1280 KiB x6, L3 12288 KiB |
| RAM | 16 GB |
| OS | Windows 11 Home 10.0.26200 |
| Compiler | g++ 16.1.0 (MinGW-w64, x86_64-posix-seh) |
| Build | CMake 4.0.2, MinGW Makefiles, `-DCMAKE_BUILD_TYPE=Release` |
| Flags | `-O3 -DNDEBUG -std=gnu++17` |
| Google Benchmark | v1.9.5, pinned via FetchContent |
| Machine idle | **record per run — see Measurement quality below** |

### Caveat: this is a hybrid laptop CPU

The i7-1255U is 2 performance cores plus 8 efficiency cores. A benchmark
thread migrated from a P-core to an E-core mid-run gets slower for reasons
that have nothing to do with the code under test, and a U-series laptop part
throttles under sustained load. Both effects are real and were observed
(see below). Treat any single run on this machine as provisional.

## Results

Nothing recorded yet. WS0.6 is blocked on measurement stability; see below.

| Benchmark | Baseline (WS0) | WS1 arena | WS2 CSR |
|---|---|---|---|
| `BM_LoadWordTrie` | — | — | — |
| `BM_SolveBoard/3x3` | — | — | — |
| `BM_SolveBoard/4x4` | — | — | — |
| `BM_SolveBoard/5x5` | — | — | — |
| `BM_EndToEnd/4x4` | — | — | — |

Report every cell as `mean ± stddev (cv%)`. A mean on its own is what made
the May "no visible improvement" question unanswerable.

### Provisional figures — NOT a baseline

Captured 2026-08-09 on a machine that was not idle. Recorded to show the
shape of the problem, not to be compared against.

```
BM_LoadWordTrie          123 ms
BM_SolveBoard/3x3       8.10 us    words=35
BM_SolveBoard/4x4       37.9 us    words=163
BM_SolveBoard/5x5       15.3 us    words=60
BM_EndToEnd/4x4          112 ms
```

The `BM_SolveBoard` figures are the trustworthy ones: they build the trie
once, outside the timed loop, and held to ~37-39 us across every run in wildly
varying machine conditions. `BM_SolveBoard/4x4` also independently reproduces
the 39,776 ns measured by the old ad-hoc harness.

The load-bearing observation stands regardless of the noise: **the search is
roughly 0.03% of end-to-end runtime.** Everything else is building a
436k-node trie from 2 MB of text on every invocation.

## Measurement quality

Two consecutive runs, unchanged tree, `--benchmark_repetitions=10`:

| Run | `BM_LoadWordTrie` | `BM_EndToEnd/4x4` |
|---|---|---|
| 1 | 122 ms, cv **4.6%** | 213 ms, cv **15.7%** |
| 2 | 158 ms, cv **36.7%** | 117 ms, cv **7.2%** |

Same binary, means moving 30-80%. The cause was environmental, not code:
three background `esbuild` processes had each accumulated ~19,000 CPU-seconds,
and the power plan was Balanced, leaving core frequency free to scale.

An earlier single-shot run reported `BM_LoadWordTrie` (123 ms) as *higher*
than `BM_EndToEnd` (112 ms), which is impossible since end-to-end contains the
load. That impossibility is what exposed the problem; without repetitions and
a stddev it would have been invisible.

### Before recording any baseline

1. Quiet the machine — no builds, no dev servers, no browser.
2. Power plan to High Performance.
3. Run the suite twice and require **cv under ~2%** on both.

Only then capture. Note that each iteration currently allocates and frees
~94 MB across 436k individual `new` calls, so run-to-run variance is partly
hostage to the OS allocator; WS1's arena is expected to shrink the variance
as well as the mean.

## Running

```powershell
# Build and run everything
.\cpp\scripts\benchmark.ps1

# Any Google Benchmark flag is forwarded to the binary
.\cpp\scripts\benchmark.ps1 --benchmark_filter=BM_SolveBoard

# Run directly once built, skipping the CMake reconfigure
.\cpp\build\bench.exe --benchmark_filter="BM_LoadWordTrie|BM_EndToEnd"

# Check whether the machine is quiet enough to trust: run twice, compare cv
.\cpp\build\bench.exe --benchmark_repetitions=10 --benchmark_report_aggregates_only=true

# Capture a baseline
.\cpp\build\bench.exe --benchmark_repetitions=10 `
    --benchmark_report_aggregates_only=true `
    --benchmark_format=json > cpp\bench\results\baseline-<date>.json
```

Diagnostic counters live behind a separate flag and must never be timed:

```powershell
.\cpp\build\main.exe tests\cpp\5.in --stats
```
