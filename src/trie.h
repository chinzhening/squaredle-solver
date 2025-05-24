#pragma once
#include <unordered_map>
#include <string>

/**
 * @brief Node structure for the Trie data structure.
 * 
 * Each node stores a flag indicating if it represents the end of a word,
 * and a map of child nodes keyed by characters.
 */
class TrieNode {
public:
    bool isEnd = false; /**< True if this node marks the end of a word. */
    std::unordered_map<char, TrieNode*> children; /**< Children nodes mapped by character. */

    /**
     * @brief Constructs a TrieNode and reserves space for 26 children.
     */
    TrieNode() {
        children.reserve(26);
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
    TrieNode* getRoot() const;

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

private:
    /**
     * @brief Recursively clears all nodes from the given node.
     * @param node The TrieNode to delete.
     */
    void clear(TrieNode* node);
};
