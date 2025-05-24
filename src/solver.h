#pragma once

#include <functional>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "trie.h"


/**
 * @brief Solves the board by finding all valid words on a letter grid using a Trie.
 * 
 * Performs a depth-first search (DFS) on an NxN board represented by a string of letters,
 * using the provided Trie to efficiently check for valid words. Words must be at least
 * 4 characters long to be included in the results.
 * 
 * @param trie Reference to a Trie containing valid words.
 * @param letters A string containing letters for the NxN board (length must be size*size).
 * @param size The side length N of the N x N board.
 * 
 * @return An unordered_set of strings representing all valid words found on the board.
 * 
 * @note The search considers adjacent letters in all 8 directions (horizontal, vertical, diagonal).
 * @note Each letter cell may be used only once per word.
 */
std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size);