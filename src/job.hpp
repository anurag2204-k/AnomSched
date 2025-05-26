#pragma once
#include <functional>
#include <chrono>

struct Job {
    int id;
    int priority;  // higher = higher priority
    std::function<void()> task;
    std::chrono::high_resolution_clock::time_point submit_time;

    Job(int id_, int prio, std::function<void()> t)
        : id(id_), priority(prio), task(std::move(t)),
          submit_time(std::chrono::high_resolution_clock::now()) {}
};

// Comparator for priority queue (max-heap by priority)
struct JobComparator {
    bool operator()(const Job& a, const Job& b) {
        return a.priority < b.priority; // higher priority first
    }
};
