#pragma once

#include <chrono>
#include <cstddef>

class Benchmark {
public:
    void start();
    void stop();
    void report(const char* label = "Benchmark");

    // Optional counters
    void reset_counters();
    void increment_recursion();
    void increment_backtrack();
    size_t get_recursion_count() const;
    size_t get_backtrack_count() const;

private:
    std::chrono::high_resolution_clock::time_point start_time, end_time;
    size_t recursion_count = 0;
    size_t backtrack_count = 0;
};