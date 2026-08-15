#include "trie.h"

#include <cstring>
#include <stdexcept>

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

namespace {

std::size_t count_nodes(const TrieNode* node) {
    std::size_t total = 1;
    for (const TrieNode* child : node->children) {
        if (child) total += count_nodes(child);
    }
    return total;
}

void serialize_node(const TrieNode* node, char incoming_char, std::vector<std::uint8_t>& out) {
    std::uint32_t mask = 0;
    for (int i = 0; i < 26; ++i) {
        if (node->children[i]) mask |= (1u << i);
    }

    out.push_back(static_cast<std::uint8_t>(incoming_char));
    out.push_back(node->isEnd ? 1 : 0);
    const auto* mask_bytes = reinterpret_cast<const std::uint8_t*>(&mask);
    out.insert(out.end(), mask_bytes, mask_bytes + sizeof(mask));

    for (int i = 0; i < 26; ++i) {
        if (node->children[i]) {
            serialize_node(node->children[i], static_cast<char>('A' + i), out);
        }
    }
}

TrieNode* deserialize_node(const std::uint8_t* data, std::size_t size, std::size_t& pos) {
    if (pos + 6 > size) {
        throw std::runtime_error("Trie::deserialize: truncated node header");
    }

    // data[pos] is the incoming char -- informational only here, since the
    // child's array slot already encodes it.
    ++pos;
    bool is_word = data[pos++] != 0;

    std::uint32_t mask;
    std::memcpy(&mask, data + pos, sizeof(mask));
    pos += sizeof(mask);

    TrieNode* node = new TrieNode();
    node->isEnd = is_word;

    for (int i = 0; i < 26; ++i) {
        if (mask & (1u << i)) {
            node->children[i] = deserialize_node(data, size, pos);
        }
    }
    return node;
}

}  // namespace

std::size_t Trie::nodeCount() const {
    return count_nodes(root);
}

std::vector<std::uint8_t> Trie::serialize() const {
    std::vector<std::uint8_t> out;
    serialize_node(root, '\0', out);
    return out;
}

Trie Trie::deserialize(const std::vector<std::uint8_t>& data) {
    Trie trie;
    delete trie.root;
    std::size_t pos = 0;
    trie.root = deserialize_node(data.data(), data.size(), pos);
    return trie;
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