#include "config.h"

#include<fstream>
#include<stdexcept>
#include<string>

#include "utils.h"

std::vector<std::string> read_words_from_files() {
    std::vector<std::string> words;

    // Reserve up front from file size (~1 word per 6 bytes, incl. newline) so
    // push_back doesn't repeatedly reallocate/move the ~197k-word vector --
    // that churn would otherwise get counted as "reading" time.
    size_t estimatedWords = 0;
    for (size_t i = 0; i < WORD_LIST_COUNT; ++i) {
        std::ifstream file(WORD_LISTS[i], std::ios::ate | std::ios::binary);
        if (file) {
            estimatedWords += static_cast<size_t>(file.tellg()) / 6;
        }
    }
    words.reserve(estimatedWords);

    for (size_t i = 0; i < WORD_LIST_COUNT; ++i) {
        std::ifstream file(WORD_LISTS[i]);
        if (!file) {
            throw std::runtime_error(std::string("Failed to open word list file: ") + WORD_LISTS[i]);
        }

        std::string word;
        while (std::getline(file, word)) {
            if (word.size() > 3) {
                words.push_back(std::move(word));
            }
        }
    }

    return words;
}

Trie build_trie_from_words(const std::vector<std::string>& words) {
    Trie trie;
    for (const auto& word : words) {
        trie.insert(word);
    }
    return trie;
}

Trie load_word_trie() {
    return build_trie_from_words(read_words_from_files());
}