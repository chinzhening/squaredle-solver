#pragma once
#include <array>
#include <cstdint>
#include <limits>
#include <string>
#include <vector>

/**
 * @brief Flat-array trie: children are indices into a single node vector
 * instead of pointers.
 *
 * Node 0 is always the root. This layout is what makes serialize()/
 * deserialize() a plain byte dump of the node vector with no pointer
 * fixup -- the on-disk bytes and the in-memory layout are the same shape,
 * which is also what makes this representation mmap-able in principle.
 */
class FlatTrie {
public:
    static constexpr std::uint32_t kNull = std::numeric_limits<std::uint32_t>::max();

    struct Node {
        bool isEnd = false;
        std::array<std::uint32_t, 26> children;

        Node() {
            children.fill(kNull);
        }
    };

    /**
     * @brief Constructs an empty trie with just the root node at index 0.
     */
    FlatTrie();

    /**
     * @brief Inserts a word into the trie.
     * @param word The string to insert.
     */
    void insert(const std::string& word);

    /**
     * @brief Searches for a word in the trie.
     * @param word The string to search for.
     * @return True if the word exists in the trie; false otherwise.
     */
    bool search(const std::string& word) const;

    /**
     * @brief Checks if there is any word in the trie that starts with the given prefix.
     * @param prefix The prefix string to check.
     * @return True if at least one word starts with the prefix; false otherwise.
     */
    bool startsWith(const std::string& prefix) const;

    /** @brief Direct access to the node vector, for the CharAutomaton adapter. */
    const std::vector<Node>& nodes() const { return nodes_; }

    /**
     * @brief Serializes the trie: a node-count header followed by a flat
     * dump of the node vector.
     */
    std::vector<std::uint8_t> serialize() const;

    /**
     * @brief Reconstructs a FlatTrie from a buffer produced by serialize().
     * @throws std::runtime_error if the buffer is truncated or malformed.
     */
    static FlatTrie deserialize(const std::vector<std::uint8_t>& data);

private:
    std::vector<Node> nodes_;
};

/**
 * @brief Adapter class to make FlatTrie conform to the CharAutomaton concept.
 */
struct FlatTrieAutomaton {
    using State = std::uint32_t;
    const FlatTrie& trie;

    FlatTrieAutomaton(const FlatTrie& t) : trie(t) {}

    State root() const;
    State transition(State s, char c) const;
    bool valid(State s) const;
    bool terminal(State s) const;
};
