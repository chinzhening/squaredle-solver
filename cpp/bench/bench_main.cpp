/**
 * @file bench_main.cpp
 * @brief Google Benchmark harness for the solver.
 *
 * Links the same solver sources the shipped binary does, with no diagnostic
 * counters compiled in -- `basic_solve_board` is called through the overload
 * that takes no SolveStats, so the DFS inner loop here is byte-for-byte the
 * one that runs in production.
 *
 * Boards are transcribed from tests/cpp rather than read at run time, so the
 * measurement contains no file I/O beyond what is being measured on purpose.
 */

#include <string>
#include <vector>

#include <benchmark/benchmark.h>

#include "solver.h"
#include "utils.h"

namespace {

struct Board {
    const char* name;
    const char* letters;
    int size;
};

// From tests/cpp/xp/3.in, tests/cpp/5.in and tests/cpp/2.in respectively.
// The 4x4 is the board every historical number in the tracker was taken on.
constexpr Board k3x3{"3x3", "DROEBPMEL", 3};
constexpr Board k4x4{"4x4", "QUAIHMTNCEIMSSCR", 4};
constexpr Board k5x5{"5x5", "SHIRTL_O_KELFTIA_Y_NBZILG", 5};

/** Builds the 436k-node trie from cpp/data/*.txt. The real hotspot. */
void BM_LoadWordTrie(benchmark::State& state) {
    for (auto _ : state) {
        Trie trie = load_word_trie();
        benchmark::DoNotOptimize(trie.getRoot());
    }
}
BENCHMARK(BM_LoadWordTrie)->Unit(benchmark::kMillisecond);

/** load_word_trie split: just the file I/O and line parsing, no trie insertion. */
void BM_ReadWordLists(benchmark::State& state) {
    for (auto _ : state) {
        std::vector<std::string> words = read_words_from_files();
        benchmark::DoNotOptimize(words);
    }
}
BENCHMARK(BM_ReadWordLists)->Unit(benchmark::kMillisecond);

/** load_word_trie split: just trie insertion, against words read once outside the timed region. */
void BM_InsertWordsIntoTrie(benchmark::State& state) {
    const std::vector<std::string> words = read_words_from_files();

    for (auto _ : state) {
        Trie trie = build_trie_from_words(words);
        benchmark::DoNotOptimize(trie.getRoot());
    }
}
BENCHMARK(BM_InsertWordsIntoTrie)->Unit(benchmark::kMillisecond);

/** Search only, against a trie built once outside the timed region. */
void BM_SolveBoard(benchmark::State& state, Board board) {
    Trie trie = load_word_trie();
    const std::string letters = board.letters;

    for (auto _ : state) {
        auto words = basic_solve_board(trie, letters, board.size);
        benchmark::DoNotOptimize(words);
    }
    state.counters["words"] = static_cast<double>(basic_solve_board(trie, letters, board.size).size());
}
BENCHMARK_CAPTURE(BM_SolveBoard, 3x3, k3x3)->Unit(benchmark::kMicrosecond);
BENCHMARK_CAPTURE(BM_SolveBoard, 4x4, k4x4)->Unit(benchmark::kMicrosecond);
BENCHMARK_CAPTURE(BM_SolveBoard, 5x5, k5x5)->Unit(benchmark::kMicrosecond);

/** Load plus solve -- the number that actually matters. */
void BM_EndToEnd(benchmark::State& state, Board board) {
    const std::string letters = board.letters;

    for (auto _ : state) {
        Trie trie = load_word_trie();
        auto words = basic_solve_board(trie, letters, board.size);
        benchmark::DoNotOptimize(words);
    }
}
BENCHMARK_CAPTURE(BM_EndToEnd, 4x4, k4x4)->Unit(benchmark::kMillisecond);

}  // namespace

BENCHMARK_MAIN();
