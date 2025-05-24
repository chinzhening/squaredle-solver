#include "solver.h"

std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size, Benchmark* bm) {
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
            if (bm) bm->increment_recursion();
            
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
            if (bm) bm->increment_backtrack();
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
