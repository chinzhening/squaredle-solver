#include "solver.h"

#include <functional>
#include <utility>

namespace {

/**
 * @brief Shared DFS body for both public overloads.
 *
 * @tparam Collect When false, every counter update is discarded at compile
 *         time by `if constexpr`, leaving the inner loop free of the `if (bm)`
 *         branch and two increments the old Benchmark hook compiled in.
 */
template <bool Collect>
std::unordered_set<std::string> solve_impl(Trie& trie, const std::string& letters, int size,
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

    std::function<void(int, int, TrieNode*, std::bitset<36>&)> dfs =
        [&] (int x, int y, TrieNode* node, std::bitset<36>& visited) {
            if constexpr (Collect) ++stats->recursions;

            // Visited in path
            if (visited[x * N + y]) {
                return;
            }

            // No valid word extension from current node
            char c = board[x][y];
            int idx = c - 'A';
            if (idx < 0 || idx >= 26 || node->children[idx] == nullptr) {
                return;
            }

            visited[x * N + y] = true;

            buffer[path_len++] = c;
            node = node->children[idx];

            // Add valid word to result
            if (node->isEnd && path_len >= 4) {
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
            dfs(i, j, trie.getRoot(), visited);
        }
    }

    return found;
}

}  // namespace

std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size) {
    return solve_impl<false>(trie, letters, size, nullptr);
}

std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size,
                                                  SolveStats& stats) {
    return solve_impl<true>(trie, letters, size, &stats);
}
