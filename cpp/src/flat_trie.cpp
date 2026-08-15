#include "flat_trie.h"

#include <cstring>
#include <stdexcept>

FlatTrie::FlatTrie() {
    nodes_.push_back(Node());  // root at index 0
}

void FlatTrie::insert(const std::string& word) {
    std::uint32_t current = 0;
    for (char ch : word) {
        if (ch < 'A' || ch > 'Z') continue;  // skip invalid chars if any

        const auto idx = static_cast<std::size_t>(ch - 'A');
        if (nodes_[current].children[idx] == kNull) {
            nodes_.push_back(Node());
            nodes_[current].children[idx] = static_cast<std::uint32_t>(nodes_.size() - 1);
        }
        current = nodes_[current].children[idx];
    }
    nodes_[current].isEnd = true;
}

bool FlatTrie::search(const std::string& word) const {
    std::uint32_t current = 0;
    for (char ch : word) {
        if (ch < 'A' || ch > 'Z') return false;

        const std::uint32_t next = nodes_[current].children[static_cast<std::size_t>(ch - 'A')];
        if (next == kNull) return false;
        current = next;
    }
    return nodes_[current].isEnd;
}

bool FlatTrie::startsWith(const std::string& prefix) const {
    std::uint32_t current = 0;
    for (char ch : prefix) {
        if (ch < 'A' || ch > 'Z') return false;

        const std::uint32_t next = nodes_[current].children[static_cast<std::size_t>(ch - 'A')];
        if (next == kNull) return false;
        current = next;
    }
    return true;
}

std::vector<std::uint8_t> FlatTrie::serialize() const {
    const auto count = static_cast<std::uint32_t>(nodes_.size());

    std::vector<std::uint8_t> out(sizeof(count) + static_cast<std::size_t>(count) * sizeof(Node));
    std::memcpy(out.data(), &count, sizeof(count));
    std::memcpy(out.data() + sizeof(count), nodes_.data(), static_cast<std::size_t>(count) * sizeof(Node));
    return out;
}

FlatTrie FlatTrie::deserialize(const std::vector<std::uint8_t>& data) {
    if (data.size() < sizeof(std::uint32_t)) {
        throw std::runtime_error("FlatTrie::deserialize: truncated header");
    }

    std::uint32_t count;
    std::memcpy(&count, data.data(), sizeof(count));

    const std::size_t expected = sizeof(count) + static_cast<std::size_t>(count) * sizeof(FlatTrie::Node);
    if (data.size() != expected) {
        throw std::runtime_error("FlatTrie::deserialize: size mismatch");
    }

    FlatTrie trie;
    trie.nodes_.resize(count);
    std::memcpy(trie.nodes_.data(), data.data() + sizeof(count), static_cast<std::size_t>(count) * sizeof(Node));
    return trie;
}

FlatTrieAutomaton::State FlatTrieAutomaton::root() const {
    return 0;
}

FlatTrieAutomaton::State FlatTrieAutomaton::transition(State s, char c) const {
    if (s == FlatTrie::kNull || c < 'A' || c > 'Z') return FlatTrie::kNull;
    return trie.nodes()[s].children[static_cast<std::size_t>(c - 'A')];
}

bool FlatTrieAutomaton::valid(State s) const {
    return s != FlatTrie::kNull;
}

bool FlatTrieAutomaton::terminal(State s) const {
    return s != FlatTrie::kNull && trie.nodes()[s].isEnd;
}
