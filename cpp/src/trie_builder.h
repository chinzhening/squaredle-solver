#pragma once

#include <concepts>
#include <string>
#include <vector>

#include "wordlist.h"

/**
 * @brief A representation computed from the whole key set at once.
 *
 * Deliberately does not require default construction: such a type
 * need not have a valid empty state.
 *
 */
template <typename T>
concept BulkBuildable = requires(const std::vector<std::string>& words) {
    { T::from_words(words) } -> std::same_as<T>;
};

/**
 * @brief Builds a trie representation from an in-memory word list.
 *
 * Insertion is the default because Trie, FlatTrie require it. A type that
 * declares from_words get that path instead. Bulk wins when a type offers both.
 *
 * Words arrive in whatever order read_words_from_files() produced.
 */
template <typename T>
T build_trie(const std::vector<std::string>& words) {
    if constexpr (BulkBuildable<T>) {
        return T::from_words(words);
    } else {
        T trie;
        for (const auto& word : words) {
            trie.insert(word);
        }
        return trie;
    }
}

/**
 * @brief Read the word lists off disk, then build.
 *
 * @throws std::runtime_error If any word list file cannot be opened.
 */
template <typename T>
T load_word_trie() {
    return build_trie<T>(read_words_from_files());
}
