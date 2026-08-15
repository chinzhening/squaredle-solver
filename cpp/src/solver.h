#pragma once

#include <bitset>
#include <cstddef>
#include <functional>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

#include "automaton.h"

/**
 * @brief Diagnostic counters for a single solve.
 *
 * Collected only by the overload that takes one. The counter-free overload
 * compiles the increments out entirely, so the timed binary is the shipped
 * binary.
 */
struct SolveStats {
    size_t recursions = 0;  /**< DFS entries, including immediate rejections. */
    size_t backtracks = 0;  /**< DFS exits that unwound a placed letter. */
};

/**
 * @brief Solves the board by finding all valid words on a letter grid using a character automaton.
 *
 * Performs a depth-first search (DFS) on an NxN board represented by a string of letters,
 * using the provided automaton to efficiently check for valid words. Words must be at least
 * 4 characters long to be included in the results.
 *
 * @param automaton Reference to a character automaton that provides word validation and transitions.
 * @param letters A string containing letters for the NxN board (length must be size*size).
 * @param size The side length N of the N x N board.
 *
 * @return An unordered_set of strings representing all valid words found on the board.
 *
 * @note The search considers adjacent letters in all 8 directions (horizontal, vertical, diagonal).
 * @note Each letter cell may be used only once per word.
 */
template<CharAutomaton A>
std::unordered_set<std::string> basic_solve_board(const A& automaton, const std::string& letters, int size);

/**
 * @brief As above, additionally accumulating diagnostic counters.
 *
 * Never time this overload: the counters sit in the DFS inner loop.
 *
 * @param stats Out parameter; incremented, not reset, by this call.
 */
template<CharAutomaton A>
std::unordered_set<std::string> basic_solve_board(const A& automaton, const std::string& letters, int size, SolveStats& stats);


/**
 * @brief Shared DFS body for both public overloads.
 *
 * @tparam Collect When false, every counter update is discarded at compile
 *         time by `if constexpr`, leaving the inner loop free of the `if (bm)`
 *         branch and two increments the old Benchmark hook compiled in.
 * @tparam A The automaton type to use for word validation.
 */
template <bool Collect, CharAutomaton A>
std::unordered_set<std::string> solve_impl(const A& automaton, const std::string& letters, int size,
                                           SolveStats* stats) {
    std::unordered_set<std::string> found;

    char buffer[20];
    int path_len = 0;

    const int N = size;
    std::vector<std::vector<char>> board(N, std::vector<char>(N));

    for (int i = 0; i < N * N; ++i) {
        board[i / N][i % N] = letters[i];
    }

    // Precompute neighbors
    std::vector<std::vector<std::pair<int, int>>> neighbor_list(N * N);
    for (int x = 0; x < N; ++x) {
        for (int y = 0; y < N; ++y) {
            int idx = x * N + y;
            for (int dx = -1; dx <= 1; ++dx) {
                for (int dy = -1; dy <= 1; ++dy) {
                    if (dx == 0 && dy == 0) continue;
                    int nx = x + dx, ny = y + dy;
                    if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                        neighbor_list[idx].emplace_back(nx, ny);
                    }
                }
            }
        }
    }

    std::function<void(int, int, typename A::State, std::bitset<36>&)> dfs =
        [&] (int x, int y, typename A::State node, std::bitset<36>& visited) {
            if constexpr (Collect) ++stats->recursions;

            // Visited in path
            if (visited[x * N + y]) {
                return;
            }

            // No valid word extension from current node
            char c = board[x][y];
            typename A::State candidate = automaton.transition(node, c);

            if (!automaton.valid(candidate)) {
                return;
            }

            visited[x * N + y] = true;

            buffer[path_len++] = c;
            node = candidate;

            // Add valid word to result
            if (automaton.terminal(candidate) && path_len >= 4) {
                found.insert(std::string(buffer, path_len));
            }

            // Search neighbors
            for (const auto& [nx, ny] : neighbor_list[x * N + y]) {
                dfs(nx, ny, node, visited);
            }

            --path_len;
            visited[x * N + y] = false;
            if constexpr (Collect) ++stats->backtracks;
        };

    std::bitset<36> visited;

    //  Run backtracking
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            dfs(i, j, automaton.root(), visited);
        }
    }

    return found;
}

template<CharAutomaton A>
std::unordered_set<std::string> basic_solve_board(const A& automaton, const std::string& letters, int size) {
    return solve_impl<false>(automaton, letters, size, nullptr);
}

template<CharAutomaton A>
std::unordered_set<std::string> basic_solve_board(const A& automaton, const std::string& letters, int size,
                                                  SolveStats& stats) {
    return solve_impl<true>(automaton, letters, size, &stats);
}
