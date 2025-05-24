#ifndef CONFIG_H
#define CONFIG_H

#include <cstddef>

constexpr const char* WORD_LISTS[] = {
    "data\\NWL2023.txt",
    "data\\long_words.txt"
};

constexpr size_t WORD_LIST_COUNT = sizeof(WORD_LISTS) / sizeof(WORD_LISTS[0]);

#endif
