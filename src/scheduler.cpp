#include "scheduler.hpp"

Scheduler::Scheduler(int num_threads, const std::string &log_filename)
    : running(false), logger(log_filename)
{
    workers.reserve(num_threads);
}

Scheduler::~Scheduler()
{
    stop();
}

void Scheduler::start()
{
    running = true;
    int thread_id = 0;
    for (; thread_id < (int)workers.capacity(); ++thread_id)
    {
        workers.emplace_back(&Scheduler::worker_loop, this, thread_id);
    }
}

void Scheduler::stop()
{
    running = false;
    condition.notify_all();
    for (auto &t : workers)
    {
        if (t.joinable())
            t.join();
    }
    workers.clear();
}

void Scheduler::submitJob(std::function<void()> task, int priority)
{
    Job job;
    job.id = ++job_counter;  // Add this line
    job.priority = priority; // Use the provided priority
    job.task = std::move(task);
    job.submit_time = std::chrono::high_resolution_clock::now();

    {
        std::lock_guard<std::mutex> lock(queue_mutex);
        job_queue.push(job);
    }
    condition.notify_one();
}

void Scheduler::worker_loop(int thread_id)
{
    while (running)
    {
        Job job(0, 0, [] {}); // default empty job

        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            condition.wait(lock, [this]
                           { return !job_queue.empty() || !running; });

            if (!running && job_queue.empty())
                return;

            job = job_queue.top();
            job_queue.pop();
        }

        auto start_time = std::chrono::high_resolution_clock::now();
        auto wait_duration = std::chrono::duration_cast<std::chrono::milliseconds>(start_time - job.submit_time).count();
        job.task();
        auto end_time = std::chrono::high_resolution_clock::now();

        // Remove the wait_duration parameter - it's calculated inside logger.log()
        logger.log(job.id, thread_id, job.submit_time, start_time, end_time);
    }
}
