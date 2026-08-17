/**
 * @file main.cpp
 * @brief Entry point for the Squaredle Solver program.
 *
 * This program takes a board on the command line, loads a word Trie, solves
 * the board to find valid words, and writes them to stdout one per line.
 */

#include <algorithm>
#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "solver.h"
#include "trie.h"
#include "trie_builder.h"

namespace {

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " <letters> <size> [--stats]\n";
}

struct Args {
    std::vector<std::string> positional;
    bool want_stats = false;
};

/**
 * @brief Parses a board size, rejecting anything std::stoi would wave through.
 *
 * stoi stops at the first non-digit, so it reads "4xyz" as 4, and reports a
 * bad string by throwing std::invalid_argument, whose what() is just "stoi".
 * Neither makes for a usable error, so parse the whole argument here.
 */
int parse_size(const std::string& arg) {
    std::size_t consumed = 0;
    int value = 0;
    try {
        value = std::stoi(arg, &consumed);
    } catch (const std::exception&) {
        throw std::runtime_error("Board size is not a number: " + arg);
    }
    if (consumed != arg.size()) {
        throw std::runtime_error("Board size is not a number: " + arg);
    }
    return value;
}

/**
 * @brief Rejects a letters string the solver could only answer with silence.
 *
 * Every cell has to be A-Z or the '_' that stands in for a blanked cell.
 * Without this a lowercase or punctuated board is not an error: the automaton
 * simply never transitions, and the run exits 0 having printed nothing, which
 * reads exactly like a board that genuinely has no words.
 */
void validate_letters(const std::string& letters) {
    for (const char c : letters) {
        if ((c < 'A' || c > 'Z') && c != '_') {
            throw std::runtime_error(
                std::string("Board letters must be A-Z or '_', found: ") + c);
        }
    }
}

Args argparse(int argc, char* argv[]) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--stats") {
            args.want_stats = true;
        } else {
            args.positional.push_back(arg);
        }
    }
    return args;
}

}

int main(int argc, char* argv[]) {
    /**
     * @brief Main program execution function.
     *
     * @param argc Number of command-line arguments.
     * @param argv Array of command-line arguments.
     *             argv[1]: letters (required)
     *             argv[2]: board size (required)
     *             --stats: report DFS counters on stderr (diagnostic only;
     *                      never time a run with this on -- see cpp/bench)
     *
     * @return 0 on success, 1 on error.
     */

    try {
        Args args = argparse(argc, argv);

        if (args.positional.size() < 2) {
            print_usage(argv[0]);
            return 1;
        }
        if (args.positional.size() > 2) {
            std::cerr << "Too many positional arguments.\n";
            print_usage(argv[0]);
            return 1;
        }

        const auto& letters = args.positional[0];
        const int boardSize = parse_size(args.positional[1]);
        const bool want_stats = args.want_stats;

        // Ordered so the bound is established before it is relied on: the
        // range check keeps the product below in range, and both run before
        // the solver indexes anything.
        if (boardSize > 6 || boardSize < 3) {
            throw std::runtime_error("boardSize must be between 3 and 6.");
        }

        if (letters.size() != boardSize * boardSize) {
            throw std::runtime_error("letters and boardSize do not match.");
        }

        validate_letters(letters);

        Trie wordTrie = load_word_trie<Trie>();
        TrieAutomaton automaton{wordTrie};

        std::unordered_set<std::string> words;
        if (want_stats) {
            SolveStats stats;
            words = basic_solve_board(automaton, letters, boardSize, stats);
            // stderr so stdout stays a clean word list
            std::cerr << "Board: " << letters << " " << boardSize << "\n"
                      << "Recursions: " << stats.recursions << "\n"
                      << "Backtracks: " << stats.backtracks << "\n";
        } else {
            words = basic_solve_board(automaton, letters, boardSize);
        }

        // Sort found words for IO
        std::vector<std::string> sorted_words(words.begin(), words.end());
        std::sort(sorted_words.begin(), sorted_words.end());

        for (const auto& word : sorted_words) {
            std::cout << word << std::endl;
        }

        return 0;

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }
}
