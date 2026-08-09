/**
 * @file main.cpp
 * @brief Entry point for the Squaredle Solver program.
 *
 * This program reads board information from a file, loads a word Trie,
 * solves the board to find valid words, and outputs the results either
 * to the console or to an output file.
 */

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "solver.h"
#include "utils.h"

namespace {

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " <board.in> [solution.out] [--stats]\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    /**
     * @brief Main program execution function.
     *
     * @param argc Number of command-line arguments.
     * @param argv Array of command-line arguments.
     *             argv[1]: input file path (required)
     *             argv[2]: output file path (optional)
     *             --stats: report DFS counters on stderr (diagnostic only;
     *                      never time a run with this on -- see cpp/bench)
     *
     * @return 0 on success, 1 on error.
     */

    try {
        bool want_stats = false;
        std::vector<const char*> positional;

        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            if (arg == "--stats") {
                want_stats = true;
            } else {
                positional.push_back(argv[i]);
            }
        }

        if (positional.empty()) {
            print_usage(argv[0]);
            return 1;
        }

        double rating;
        std::string letters;
        int boardSize;

        read_board_info(positional[0], rating, letters, boardSize);

        Trie wordTrie = load_word_trie();

        std::unordered_set<std::string> words;
        if (want_stats) {
            SolveStats stats;
            words = basic_solve_board(wordTrie, letters, boardSize, stats);
            // stderr so stdout stays a clean word list
            std::cerr << "Board: " << letters << " " << boardSize << "\n"
                      << "Recursions: " << stats.recursions << "\n"
                      << "Backtracks: " << stats.backtracks << "\n";
        } else {
            words = basic_solve_board(wordTrie, letters, boardSize);
        }

        // Sort found words for IO
        std::vector<std::string> sorted_words(words.begin(), words.end());
        std::sort(sorted_words.begin(), sorted_words.end());

        if (positional.size() >= 2) {
            std::ofstream out(positional[1]);
            for (const auto& word : sorted_words) {
                out << word << std::endl;
            }
        } else {
            for (const auto& word : sorted_words) {
                std::cout << word << std::endl;
            }
        }

        return 0;

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }
}
