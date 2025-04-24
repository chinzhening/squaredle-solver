#include <iostream>
#include <fstream>

#include <algorithm>

#include "basic_algorithm.cpp"
//#include "other_algorithm.cpp"

void read_board_info(const std::string& path, double& rating, std::string& letters) {
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Failed to open board_info.txt");
    file >> rating >> letters;
}

Trie load_word_trie() {
    const char* word_lists[] = {
        "data\\NWL2023.txt",
        "data\\long_words.txt"
    };

    Trie trie;

    for (const char* path : word_lists) {
        std::ifstream file(path);
        if (!file) {
            throw std::runtime_error(std::string("Failed to open word list file: ") + path);
        }

        std::string word;
        while (std::getline(file, word)) {
            if (word.size() > 3) {
                trie.insert(word);
            }
        }
    }

    return trie;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage:  <board_info.txt> <solution.txt>" << std::endl;
        return 1;
    }

    try {
        double rating;
        std::string letters;

        read_board_info(argv[1], rating, letters);

        Trie wordTrie = load_word_trie();

        std::unordered_set<std::string> words = basic_solve_board(wordTrie, letters);

        // sort found words
        std::vector<std::string> sorted_words(words.begin(), words.end());
        std::sort(sorted_words.begin(), sorted_words.end());

        std::ofstream out(argv[2]);
        for (const auto& word : sorted_words) {
            out << word << std::endl;
        }

        return 0;
    
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

}