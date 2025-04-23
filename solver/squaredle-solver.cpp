#include <iostream>
#include <fstream>

#include <functional>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "Trie.h"

void readBoardInfo(const std::string& path, double& rating, std::string& letters) {
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Failed to open board_info.txt");
    file >> rating >> letters;
}

Trie loadWordTrie(const std::string& path) {
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Failed to open word list file");

    Trie trie;
    std::string line;

    while (std::getline(file, line)) {
        size_t spacePos = line.find(' ');
        if (spacePos != std::string::npos && spacePos > 3) {
            trie.insert(line.substr(0, spacePos));
        }
    }

    return trie;
}

std::unordered_set<std::string> solveBoard(Trie& trie, const std::string& letters) {
    std::unordered_set<std::string> found;
    std::string path;

    const int N = 4;  
    char board[N][N]; 

    for (int i = 0; i < N * N; ++i) {
        board[i / N][i % N] = letters[i];
    }

    // Backtracking algorithm
    std::function<void(int, int, TrieNode*, std::unordered_set<int>&)> dfs = 
        [&] (int x, int y, TrieNode* node, std::unordered_set<int>& visited) {
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

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: squaredle-solver <board_info.txt> <word_list.txt> <solution.txt>" << std::endl;
        return 1;
    }

    try {
        double rating;
        std::string letters;

        readBoardInfo(argv[1], rating, letters);

        Trie wordTrie = loadWordTrie(argv[2]);

        std::unordered_set<std::string> solution = solveBoard(wordTrie, letters);

        std::ofstream out(argv[3]);
        for (const auto& word : solution) {
            out << word << std::endl;
        }


        return 0;
    
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

}