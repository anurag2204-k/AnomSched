#ifndef SCHEDULER_HPP
#define SCHEDULER_HPP

#include <functional>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <chrono>
#include "logger.hpp"

// ------------------- Job Definition ---------------------
struct Job
{
    int id;
    int priority;
    std::function<void()> task;
    std::chrono::high_resolution_clock::time_point submit_time;

    // Default constructor
    Job() : id(0), priority(0), task([] {}), submit_time(std::chrono::high_resolution_clock::now()) {}

    // Parameterized constructor
    Job(int id_, int prio, std::function<void()> t)
        : id(id_), priority(prio), task(std::move(t)), submit_time(std::chrono::high_resolution_clock::now()) {}

    // For priority queue comparison (higher priority = run first)
    bool operator<(const Job &other) const
    {
        return priority < other.priority;
    }
};

// ------------------- Scheduler Class ---------------------
class Scheduler
{
public:
    Scheduler(int num_threads, const std::string &log_filename); // Add log_filename parameter
    ~Scheduler();

    void start();
    void stop();
    void submitJob(std::function<void()> task, int priority = 0);

private:
    void worker_loop(int thread_id); // Match the implementation name

    std::vector<std::thread> workers;
    std::priority_queue<Job> job_queue;
    std::mutex queue_mutex;
    std::condition_variable condition;
    std::atomic<bool> running;
    std::atomic<int> job_counter{0}; // Add this line

    Logger logger; // Handles logging of execution metrics
};

#endif // SCHEDULER_HPP
