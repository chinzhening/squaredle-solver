#pragma once

#include <string>
#include <vector>
#include "trie.h"  // Include if Trie is defined in a separate header

/**
 * @brief Reads words from the predefined word list files.
 *
 * @return All words (longer than 3 characters) from the word list files, in file order.
 *
 * @throws std::runtime_error If any word list file cannot be opened.
 */
std::vector<std::string> read_words_from_files();

/**
 * @brief Inserts a collection of words into a new Trie.
 *
 * @param words Words to insert.
 * @return A Trie populated with the given words.
 */
Trie build_trie_from_words(const std::vector<std::string>& words);

/**
 * @brief Loads a Trie with words from predefined word list files.
 *
 * @return A Trie populated with words from the word list files.
 *
 * @throws std::runtime_error If any word list file cannot be opened.
 */
Trie load_word_trie();
