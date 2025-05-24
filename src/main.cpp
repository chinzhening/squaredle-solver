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

#include "solver.h"
#include "utils.h"

#include "benchmark.h"

int main(int argc, char* argv[]) {
    /**
     * @brief Main program execution function.
     *
     * @param argc Number of command-line arguments.
     * @param argv Array of command-line arguments.
     *             argv[1]: input file path (required)
     *             argv[2]: output file path (optional)
     *
     * @return 0 on success, 1 on error.
     */

    try {
        double rating;
        std::string letters;
        int boardSize;

        read_board_info(argv[1], rating, letters, boardSize);

        Trie wordTrie = load_word_trie();

        std::unordered_set<std::string> words;
        #ifdef ENABLE_BENCHMARKING
            Benchmark bm;
            bm.reset_counters();
            bm.start();
            words = basic_solve_board(wordTrie, letters, boardSize, &bm);
            bm.stop();
            bm.report();
        #else
            words = basic_solve_board(wordTrie, letters, boardSize, nullptr);

            // Sort found words for IO
            std::vector<std::string> sorted_words(words.begin(), words.end());
            std::sort(sorted_words.begin(), sorted_words.end());

            
            if (argc == 3){
                std::ofstream out(argv[2]);
                for (const auto& word : sorted_words) {
                    out << word << std::endl;
                }
            } else if (argc == 2) {
                for (const auto& word : sorted_words) {
                    std::cout << word << std::endl;
                }
            }
            
            return 0;
        #endif
    
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

}