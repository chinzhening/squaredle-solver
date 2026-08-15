#include "trie.h"

Trie::Trie() {
    root = new TrieNode();
}

Trie::~Trie() {
    delete root;
}

const TrieNode* Trie::getRoot() const {
    return root;
}

void Trie::insert(const std::string& word) {
    TrieNode* current = root;
    for (char ch : word) {
        if (ch < 'A' || ch > 'Z') continue; // skip invalid chars if any

        int idx = ch - 'A';
        if (!current->children[idx]) {
            current->children[idx] = new TrieNode();
        }
        current = current->children[idx];
    }
    current->isEnd = true;
}

bool Trie::search(const std::string& word) const {
    TrieNode* current = root;
    for (char ch : word) {
        if (ch < 'A' || ch > 'Z') return false;

        int idx = ch - 'A';
        if (!current->children[idx]) return false;
        current = current->children[idx];
    }
    return current->isEnd;
}

bool Trie::startsWith(const std::string& prefix) const {
    TrieNode* current = root;
    for (char ch : prefix) {
        if (ch < 'A' || ch > 'Z') return false;

        int idx = ch - 'A';
        if (!current->children[idx]) return false;
        current = current->children[idx];
    }
    return true;
}

TrieAutomaton::State TrieAutomaton::root() const {
    return trie.getRoot();
}

TrieAutomaton::State TrieAutomaton::transition(TrieAutomaton::State s, char c) const {
    if (!s || c < 'A' || c > 'Z') return nullptr;

    const auto index = static_cast<std::size_t>(c - 'A');
    return s->children[index];
}

bool TrieAutomaton::valid(TrieAutomaton::State s) const {
    return s != nullptr;
}

bool TrieAutomaton::terminal(TrieAutomaton::State s) const {
    return s && s->isEnd;
}