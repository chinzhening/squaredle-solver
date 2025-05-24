#include "config.h"

#include<fstream>
#include<stdexcept>
#include<string>

#include "utils.h"

void read_board_info(const std::string& path, double& rating, std::string& letters, int& boardSize) {
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Failed to open: " + path);
    file >> rating >> letters >> boardSize;
}


Trie load_word_trie() {
    Trie trie;

    for (size_t i = 0; i < WORD_LIST_COUNT; ++i) {
        std::ifstream file(WORD_LISTS[i]);
        if (!file) {
            throw std::runtime_error(std::string("Failed to open word list file: ") + WORD_LISTS[i]);
        }

        std::string word;
        while (std::getline(file, word)) {
            if (word.size() > 3) {
                trie.insert(word);
            }
        }
    }

    return trie;
}