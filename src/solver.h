#pragma once

#include <functional>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "trie.h"

std::unordered_set<std::string> basic_solve_board(Trie& trie, const std::string& letters, int size);