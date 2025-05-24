#include "trie.h"

Trie::Trie() {
    root = new TrieNode();
}

Trie::~Trie() {
    clear(root);
}

TrieNode* Trie::getRoot() const {
    return root;
}

void Trie::insert(const std::string& word) {
    TrieNode* node = root;
    for (char c : word) {
        if (!node->children.count(c)) {
            node->children[c] = new TrieNode();
        }
        node = node->children[c];
    }
    node->isEnd = true;
}

bool Trie::search(const std::string& word) const {
    TrieNode* node = root;
    for (char c : word) {
        if (!node->children.count(c)) return false;
        node = node->children.at(c);
    }
    return node->isEnd;
}

bool Trie::startsWith(const std::string& prefix) const {
    TrieNode* node = root;
    for (char c : prefix) {
        if (!node->children.count(c)) return false;
        node = node->children.at(c);
    }
    return true;
}

void Trie::clear(TrieNode* node) {
    for (auto& [_, child] : node->children) {
        clear(child);
    }
    delete node;
}
