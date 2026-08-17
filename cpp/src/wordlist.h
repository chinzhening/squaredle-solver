#pragma once

#include <string>
#include <vector>


/**
 * @brief Reads words from the predefined word list files.
 *
 * @return All words (> 3 chars) from the wordlist files in file order.
 *
 * @throws std::runtime_error If any wordlist file cannot be opened.
 */
std::vector<std::string> read_words_from_files();
