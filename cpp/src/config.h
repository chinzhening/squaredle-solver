#pragma once
#include <cstddef>

#ifndef DATA_DIR
#define DATA_DIR "data"
#endif

constexpr const char* WORD_LISTS[] = {
    DATA_DIR "/NWL2023.txt",
    DATA_DIR "/long_words.txt"
};

constexpr size_t WORD_LIST_COUNT = sizeof(WORD_LISTS) / sizeof(WORD_LISTS[0]);
