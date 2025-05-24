#include "solver.h"

std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size, Benchmark* bm) {
    std::unordered_set<std::string> found;
    std::string path;

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

    std::function<void(int, int, TrieNode*, std::vector<bool>&)> dfs = 
        [&] (int x, int y, TrieNode* node, std::vector<bool>& visited) {
            if (bm) bm->increment_recursion();
            
            // Visited in path
            if (visited[x * N + y]) {
                return;  
            }

            // No valid word extension from current node
            char c = board[x][y];
            if (!node->children.count(c)) {
                return;  
            }

            visited[x * N + y] = true;

            path.push_back(c);
            node = node->children[c];

            // Add valid word to result
            if (node->isEnd && path.length() >= 4) {
                found.insert(path);
            }

            // Search neighbors
            for (const auto& [nx, ny] : neighbor_list[x * N + y]) {
                dfs(nx, ny, node, visited);
            }

            path.pop_back();
            visited[x * N + y] = false;
            if (bm) bm->increment_backtrack();
        };

    std::vector<bool> visited(N*N, false);

    //  Run backtracking
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            dfs(i, j, trie.getRoot(), visited);
        }
    }

    return found;
}
