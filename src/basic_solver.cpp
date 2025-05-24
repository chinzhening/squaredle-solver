#include "solver.h"

std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size, Benchmark* bm) {
    std::unordered_set<std::string> found;
    std::string path;

    const int N = size;  
    std::vector<std::vector<char>> board(N, std::vector<char>(N));

    for (int i = 0; i < N * N; ++i) {
        board[i / N][i % N] = letters[i];
    }

    std::function<void(int, int, TrieNode*, std::unordered_set<int>&)> dfs = 
        [&] (int x, int y, TrieNode* node, std::unordered_set<int>& visited) {
            if (bm) bm->increment_recursion();
            // Out of bounds
            if (x < 0 || y < 0) {
                return;
            }
            if (x >= N || y >= N) {
                return;
            }
            // Visited in path
            if (visited.find(x * N + y) != visited.end()) {
                return;  
            }

            // No valid word extension from current node
            char c = board[x][y];
            if (!node->children.count(c)) {
                return;  
            }

            visited.insert(x * N + y);

            path.push_back(c);
            node = node->children[c];

            // Add valid word to result
            if (node->isEnd && path.length() >= 4) {
                found.insert(path);
            }

            // Search neighbors
            for (int dx = -1; dx <= 1; ++dx) {
                for (int dy = -1; dy <= 1; ++dy) {
                    if (dx || dy) {
                        dfs(x + dx, y + dy, node, visited);
                    }
                }
            }

            path.pop_back();
            visited.erase(x * N + y);
            if (bm) bm->increment_backtrack();
        };

    std::unordered_set<int> visited;

    //  Run backtracking
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            dfs(i, j, trie.getRoot(), visited);
        }
    }

    return found;
}
