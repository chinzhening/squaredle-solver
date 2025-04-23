#pragma once
#include <unordered_map>
#include <string>

class TrieNode {
public:
    bool isEnd = false;
    std::unordered_map<char, TrieNode*> children;

    TrieNode() {
        children.reserve(26);
    }
};

class Trie {
private:
    TrieNode* root;

public:
    Trie();
    ~Trie();

    TrieNode* getRoot() const;

    void insert(const std::string& word);
    bool search(const std::string& word) const;
    bool startsWith(const std::string& prefix) const;

private:
    void clear(TrieNode* node);
};
