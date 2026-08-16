/**
 * @file bench_main.cpp
 * @brief Google Benchmark harness for the solver.
 *
 * Links the same solver sources the shipped binary does, with no diagnostic
 * counters compiled in -- `basic_solve_board` is called through the overload
 * that takes no SolveStats, so the DFS inner loop here is byte-for-byte the
 * one that runs in production.
 *
 * Every benchmark body is a template over the trie representation, so the
 * pointer trie and the flat-array trie are measured by literally the same
 * code. That is the point: it keeps the comparison about the data structures
 * rather than about incidental differences between hand-written benchmark
 * bodies.
 *
 * Benchmark *names* are registered explicitly rather than via
 * BENCHMARK_TEMPLATE, which would mangle them to `BM_SolveBoard<Trie>/4x4`.
 * The pointer-trie names are load-bearing: bench/RESULTS.md tracks WS0
 * baselines under the historical names, and renaming them would silently
 * break comparability with every committed JSON run.
 *
 * Boards are transcribed from tests/boards rather than read at run time, so the
 * measurement contains no file I/O beyond what is being measured on purpose.
 */

#include <cstddef>
#include <string>
#include <vector>

#include <benchmark/benchmark.h>

#include "flat_trie.h"
#include "solver.h"
#include "trie.h"
#include "utils.h"

#ifdef _WIN32
// Order matters: windows.h must precede psapi.h.
#include <windows.h>

#include <psapi.h>
#endif

namespace {

struct Board {
    const char* name;
    const char* letters;
    int size;
};

// From tests/boards/express-3x3-a.in, benchmark-4x4.in and blanked-5x5.in.
// These are transcribed copies: change a fixture and the benchmark keeps
// measuring the old board until these constants are updated too.
// The 4x4 is the board every historical number in the tracker was taken on.
constexpr Board k3x3{"3x3", "DROEBPMEL", 3};
constexpr Board k4x4{"4x4", "QUAIHMTNCEIMSSCR", 4};
constexpr Board k5x5{"5x5", "SHIRTL_O_KELFTIA_Y_NBZILG", 5};

// ---------------------------------------------------------------------------
// Representation traits
// ---------------------------------------------------------------------------

/**
 * @brief Per-representation glue: which automaton adapts it, and an O(1)
 * handle to keep a built trie from being optimised away.
 *
 * The handle has to be O(1): calling something like nodeCount() inside a
 * timed loop would fold an O(nodes) walk into the number being reported.
 */
template <typename T>
struct Representation;

template <>
struct Representation<Trie> {
    using Automaton = TrieAutomaton;
    static const void* handle(const Trie& t) { return t.getRoot(); }
};

template <>
struct Representation<FlatTrie> {
    using Automaton = FlatTrieAutomaton;
    static const void* handle(const FlatTrie& t) { return t.nodes().data(); }
};

template <typename T>
using AutomatonFor = typename Representation<T>::Automaton;

/** Builds any representation from an in-memory word list. */
template <typename T>
T build_from_words(const std::vector<std::string>& words) {
    T trie;
    for (const auto& word : words) {
        trie.insert(word);
    }
    return trie;
}

/** Read the word lists and build: the full cold load path. */
template <typename T>
T load_trie() {
    return build_from_words<T>(read_words_from_files());
}

/**
 * @brief Current working-set size, or 0 where unsupported.
 *
 * Working set is an approximation of RSS: it excludes paged-out pages and
 * includes allocator slack, so treat the deltas below as indicative rather
 * than exact heap accounting. It is the one metric Google Benchmark has no
 * native support for.
 */
std::size_t current_rss_bytes() {
#ifdef _WIN32
    PROCESS_MEMORY_COUNTERS pmc{};
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return static_cast<std::size_t>(pmc.WorkingSetSize);
    }
#endif
    return 0;
}

constexpr double kBytesPerMiB = 1024.0 * 1024.0;

// ---------------------------------------------------------------------------
// Benchmarks
// ---------------------------------------------------------------------------

/** Read the word lists and build the trie. Representation-independent I/O included. */
template <typename T>
void BM_Load(benchmark::State& state) {
    for (auto _ : state) {
        T trie = load_trie<T>();
        benchmark::DoNotOptimize(Representation<T>::handle(trie));
    }
}

/** Load split: just the file I/O and line parsing, no trie insertion. */
void BM_ReadWordLists(benchmark::State& state) {
    for (auto _ : state) {
        std::vector<std::string> words = read_words_from_files();
        benchmark::DoNotOptimize(words);
    }
}

/** Load split: just insertion, against words read once outside the timed region. */
template <typename T>
void BM_Insert(benchmark::State& state) {
    const std::vector<std::string> words = read_words_from_files();

    for (auto _ : state) {
        T trie = build_from_words<T>(words);
        benchmark::DoNotOptimize(Representation<T>::handle(trie));
    }
}

/** Serialize only, against a trie built once outside the timed region. */
template <typename T>
void BM_Serialize(benchmark::State& state) {
    const T trie = load_trie<T>();

    for (auto _ : state) {
        auto bytes = trie.serialize();
        benchmark::DoNotOptimize(bytes);
    }
    // Size is reported, never timed.
    state.counters["bytes"] = static_cast<double>(trie.serialize().size());
}

/** Deserialize only, against a buffer produced once outside the timed region. */
template <typename T>
void BM_Deserialize(benchmark::State& state) {
    const T trie = load_trie<T>();
    const auto bytes = trie.serialize();

    for (auto _ : state) {
        T restored = T::deserialize(bytes);
        benchmark::DoNotOptimize(Representation<T>::handle(restored));
    }
    state.counters["bytes"] = static_cast<double>(bytes.size());
}

/** Search only, against a trie built once outside the timed region. */
template <typename T>
void BM_Solve(benchmark::State& state, Board board) {
    const T trie = load_trie<T>();
    const AutomatonFor<T> automaton{trie};
    const std::string letters = board.letters;

    for (auto _ : state) {
        auto words = basic_solve_board(automaton, letters, board.size);
        benchmark::DoNotOptimize(words);
    }

    // Counters come from a separate untimed run through the SolveStats
    // overload. The timed loop above must keep using the counter-free
    // overload, or the increments land in the inner loop being measured.
    SolveStats stats;
    const auto words = basic_solve_board(automaton, letters, board.size, stats);
    state.counters["words"] = static_cast<double>(words.size());
    state.counters["transitions"] = static_cast<double>(stats.transitions);
}

/** Load plus solve -- the number that actually matters. */
template <typename T>
void BM_EndToEnd(benchmark::State& state, Board board) {
    const std::string letters = board.letters;

    for (auto _ : state) {
        T trie = load_trie<T>();
        const AutomatonFor<T> automaton{trie};
        auto words = basic_solve_board(automaton, letters, board.size);
        benchmark::DoNotOptimize(words);
    }
}

/**
 * @brief Structural cost of one built trie: working-set delta, node count,
 * serialized size.
 *
 * Registered with a single iteration -- the reported time is meaningless
 * here, only the counters matter. Measuring across more iterations would
 * report the delta of an already-warm allocator rather than of the trie.
 */
template <typename T>
void BM_Footprint(benchmark::State& state) {
    const std::vector<std::string> words = read_words_from_files();

    for (auto _ : state) {
        const std::size_t before = current_rss_bytes();
        T trie = build_from_words<T>(words);
        const std::size_t after = current_rss_bytes();

        state.counters["rss_delta_mib"] =
            after > before ? static_cast<double>(after - before) / kBytesPerMiB : 0.0;
        state.counters["nodes"] = static_cast<double>(trie.nodeCount());
        state.counters["serialized_mib"] = static_cast<double>(trie.serialize().size()) / kBytesPerMiB;

        benchmark::DoNotOptimize(Representation<T>::handle(trie));
    }
}

// ---------------------------------------------------------------------------
// Registration
// ---------------------------------------------------------------------------

void register_benchmarks() {
    using benchmark::RegisterBenchmark;
    const auto ms = benchmark::kMillisecond;
    const auto us = benchmark::kMicrosecond;

    // Pointer trie -- names frozen to match bench/RESULTS.md history.
    RegisterBenchmark("BM_LoadWordTrie", BM_Load<Trie>)->Unit(ms);
    RegisterBenchmark("BM_ReadWordLists", BM_ReadWordLists)->Unit(ms);
    RegisterBenchmark("BM_InsertWordsIntoTrie", BM_Insert<Trie>)->Unit(ms);
    RegisterBenchmark("BM_SerializeTrie", BM_Serialize<Trie>)->Unit(ms);
    RegisterBenchmark("BM_DeserializeTrie", BM_Deserialize<Trie>)->Unit(ms);
    RegisterBenchmark("BM_SolveBoard/3x3", BM_Solve<Trie>, k3x3)->Unit(us);
    RegisterBenchmark("BM_SolveBoard/4x4", BM_Solve<Trie>, k4x4)->Unit(us);
    RegisterBenchmark("BM_SolveBoard/5x5", BM_Solve<Trie>, k5x5)->Unit(us);
    RegisterBenchmark("BM_EndToEnd/4x4", BM_EndToEnd<Trie>, k4x4)->Unit(ms);
    RegisterBenchmark("BM_Footprint/pointer", BM_Footprint<Trie>)->Unit(ms)->Iterations(1);

    // Flat-array trie -- parallel names, no history to preserve.
    RegisterBenchmark("BM_LoadFlatWordTrie", BM_Load<FlatTrie>)->Unit(ms);
    RegisterBenchmark("BM_InsertWordsIntoFlatTrie", BM_Insert<FlatTrie>)->Unit(ms);
    RegisterBenchmark("BM_SerializeFlatTrie", BM_Serialize<FlatTrie>)->Unit(ms);
    RegisterBenchmark("BM_DeserializeFlatTrie", BM_Deserialize<FlatTrie>)->Unit(ms);
    RegisterBenchmark("BM_SolveFlatBoard/3x3", BM_Solve<FlatTrie>, k3x3)->Unit(us);
    RegisterBenchmark("BM_SolveFlatBoard/4x4", BM_Solve<FlatTrie>, k4x4)->Unit(us);
    RegisterBenchmark("BM_SolveFlatBoard/5x5", BM_Solve<FlatTrie>, k5x5)->Unit(us);
    RegisterBenchmark("BM_EndToEndFlat/4x4", BM_EndToEnd<FlatTrie>, k4x4)->Unit(ms);
    RegisterBenchmark("BM_Footprint/flat", BM_Footprint<FlatTrie>)->Unit(ms)->Iterations(1);
}

}  // namespace

// Hand-rolled equivalent of BENCHMARK_MAIN(), so registration can run first.
int main(int argc, char** argv) {
    register_benchmarks();

    benchmark::Initialize(&argc, argv);
    if (benchmark::ReportUnrecognizedArguments(argc, argv)) {
        return 1;
    }
    benchmark::RunSpecifiedBenchmarks();
    benchmark::Shutdown();
    return 0;
}
