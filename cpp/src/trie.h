#pragma once
#include <array>
#include <cstdint>
#include <string>
#include <vector>

/**
 * @brief Node structure for the Trie data structure.
 * 
 * Each node stores a flag indicating if it represents the end of a word,
 * and a map of child nodes keyed by characters.
 */
class TrieNode {
public:
    bool isEnd = false; /**< True if this node marks the end of a word. */
    std::array<TrieNode*, 26> children; /**< Children nodes mapped by character. */

    /**
     * @brief Constructs a TrieNode and reserves space for 26 children.
     */
    TrieNode() {
        children.fill(nullptr);
    }

    ~TrieNode() {
        for (TrieNode* child : children) {
            delete child;
        }
    }
};

/**
 * @brief Trie data structure for efficient insertion and search of strings.
 */
class Trie {
private:
    TrieNode* root; /**< Root node of the Trie. */

public:
    /**
     * @brief Constructs an empty Trie.
     */
    Trie();

    /**
     * @brief Destructor to clean up allocated nodes.
     */
    ~Trie();

    /**
     * @brief Returns a pointer to the root node.
     * @return Pointer to the root TrieNode.
     */
    const TrieNode* getRoot() const;

    /**
     * @brief Inserts a word into the Trie.
     * @param word The string to insert.
     */
    void insert(const std::string& word);

    /**
     * @brief Searches for a word in the Trie.
     * @param word The string to search for.
     * @return True if the word exists in the Trie; false otherwise.
     */
    bool search(const std::string& word) const;

    /**
     * @brief Checks if there is any word in the Trie that starts with the given prefix.
     * @param prefix The prefix string to check.
     * @return True if at least one word starts with the prefix; false otherwise.
     */
    bool startsWith(const std::string& prefix) const;

    /**
     * @brief Serializes the trie to a byte buffer via pre-order DFS.
     *
     * Each node is written as: incoming char (1 byte), is_word (1 byte),
     * children bitmask (4 bytes, bit i set iff children[i] != nullptr).
     * Children are then emitted in bitmask order, recursively.
     */
    std::vector<std::uint8_t> serialize() const;

    /**
     * @brief Reconstructs a Trie from a buffer produced by serialize().
     * @throws std::runtime_error if the buffer is truncated or malformed.
     */
    static Trie deserialize(const std::vector<std::uint8_t>& data);
};

/**
 * @brief Adapter class to make Trie conform to the CharAutomaton concept.
 */
struct TrieAutomaton {
    using State = const TrieNode*;
    const Trie& trie;

    TrieAutomaton(const Trie& t) : trie(t) {}

    State root() const;
    State transition(State s, char c) const;
    bool valid(State s) const;
    bool terminal(State s) const;

};