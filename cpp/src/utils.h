#ifndef UTILS_H
#define UTILS_H

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

/**
 * @brief Reads board information from a file.
 * 
 * @param path Path to the input file.
 * @param rating Output parameter to store the board's difficulty rating.
 * @param letters Output parameter to store the board's letter layout as a string.
 * @param boardSize Output parameter to store the board's dimension (e.g., 5 for a 5x5 board).
 * 
 * @throws std::runtime_error If the file cannot be opened.
 */
void read_board_info(const std::string& path, double& rating, std::string& letters, int& boardSize);

#endif // UTILS_H
