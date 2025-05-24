#include "benchmark.h"
#include <iostream>

#ifdef ENABLE_BENCHMARKING

void Benchmark::start() {
    start_time = std::chrono::high_resolution_clock::now();
}

void Benchmark::stop() {
    end_time = std::chrono::high_resolution_clock::now();
}

void Benchmark::report(const char* label) {
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time).count();
    std::cout << label << ": " << duration << " ns\n";
    std::cout << "Recursions: " << recursion_count << ", Backtracks: " << backtrack_count << '\n';
}

void Benchmark::reset_counters() {
    recursion_count = backtrack_count = 0;
}

void Benchmark::increment_recursion() { ++recursion_count; }
void Benchmark::increment_backtrack() { ++backtrack_count; }
size_t Benchmark::get_recursion_count() const { return recursion_count; }
size_t Benchmark::get_backtrack_count() const { return backtrack_count; }


#else

// No-op versions
void Benchmark::start() {}
void Benchmark::stop() {}
void Benchmark::report(const char*) {}

void Benchmark::reset_counters() {}
void Benchmark::increment_recursion() {}
void Benchmark::increment_backtrack() {}
size_t Benchmark::get_recursion_count() const { return 0; }
size_t Benchmark::get_backtrack_count() const { return 0; }

#endif
