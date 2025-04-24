#include <iostream>
#include <fstream>

#include "basic_algorithm.cpp"
//#include "other_algorithm.cpp"

void read_board_info(const std::string& path, double& rating, std::string& letters) {
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Failed to open board_info.txt");
    file >> rating >> letters;
}

Trie load_word_trie(const std::string& path) {
    std::ifstream file(path);
    if (!file)
        throw std::runtime_error("Failed to open word list file");

    Trie trie;
    std::string line;

    while (std::getline(file, line)) {
        size_t spacePos = line.find(' ');
        if (spacePos != std::string::npos && spacePos > 3) {
            trie.insert(line.substr(0, spacePos));
        }
    }

    return trie;
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage:  <board_info.txt> <word_list.txt> <solution.txt>" << std::endl;
        return 1;
    }

    try {
        double rating;
        std::string letters;

        read_board_info(argv[1], rating, letters);

        Trie wordTrie = load_word_trie(argv[2]);

        std::unordered_set<std::string> solution = basic_solve_board(wordTrie, letters);

        std::ofstream out(argv[3]);
        for (const auto& word : solution) {
            out << word << std::endl;
        }

        return 0;
    
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

}