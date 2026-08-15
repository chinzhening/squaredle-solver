#pragma once
#include <cstdint>
#include <vector>

template <typename T>
concept Serializable = requires(T t, std::vector<std::uint8_t>& bytes) {
    { t.serialize() } -> std::same_as<std::vector<std::uint8_t>>;
    { T::deserialize(bytes) } -> std::same_as<T>;
};