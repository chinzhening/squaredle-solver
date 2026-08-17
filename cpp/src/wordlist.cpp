#include "wordlist.h"

#include <array>
#include <fstream>
#include <stdexcept>

// Outside the anonymous namespace below because a macro has no notion of one:
// the preprocessor runs before any of this is parsed, so putting it inside
// would only read as though it were scoped.
//
// CMake supplies the real path via target_compile_definitions. The relative
// fallback covers a compile that does not go through CMake at all, where it
// resolves against the working directory rather than the binary.
#ifndef DATA_DIR
#define DATA_DIR "data"
#endif

namespace {

constexpr std::array WORD_LISTS{
    DATA_DIR "/NWL2023.txt",
    DATA_DIR "/long_words.txt",
};

}

std::vector<std::string> read_words_from_files() {
    std::vector<std::string> words;

    // Reserve up front from file size (~1 word per 6 bytes, incl. newline) so
    // push_back doesn't repeatedly reallocate/move the ~197k-word vector --
    // that churn would otherwise get counted as "reading" time.
    size_t estimatedWords = 0;
    for (const char* path : WORD_LISTS) {
        std::ifstream file(path, std::ios::ate | std::ios::binary);
        if (file) {
            estimatedWords += static_cast<size_t>(file.tellg()) / 6;
        }
    }
    words.reserve(estimatedWords);

    for (const char* path : WORD_LISTS) {
        std::ifstream file(path);
        if (!file) {
            throw std::runtime_error(std::string("Failed to open word list file: ") + path);
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
