#pragma once
#include <concepts>

/**
 * CharAutomaton is an abstraction interface for all the Trie-like data
 * structures.
 */
template <typename T>
concept CharAutomaton = requires(const T& t, typename T::State s, char c) {
    { t.root() } -> std::same_as<typename T::State>;
    { t.transition(s, c) } -> std::same_as<typename T::State>;
    { t.valid(s) } -> std::same_as<bool>;
    { t.terminal(s) } -> std::same_as<bool>;
};

// First time using concepts in C++20, so this is just documents what this
// means, and why I used it here.

// CharAutomaton<T> compiles if:
// - T has a nested type named 'State'.
// - T has 4 member functions: root(), transition(State, char), valid(State),
//   and terminal(State).
// - Each has to satisfy the return type requirements.
//
// Note: std::same_as checks for exact type equality at compile time.

// I used this concept to constrain the template parameter of the functions
// that operate on Trie-like data structures, ensuring that they only accept
// types that conform to the CharAutomaton interface.
//
// This helps catch errors at compile time and provides better code clarity and
// maintainability.
//
// Before this abstraction interface, basic_solver.cpp is coupled to the
// pointer-Trie implementation, which makes it hard to swap out the Trie for a
// different data structure. This makes it difficult to benchmark different
// implementations.