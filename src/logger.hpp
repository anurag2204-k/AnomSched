#pragma once
#include <fstream>
#include <mutex>
#include <string>
#include <chrono>
#include <iomanip>
#include <vector>
#include <numeric>
#include <iostream>
#include <cmath> // Add this line for std::sqrt

class Logger
{
    std::mutex log_mutex;
    std::ofstream log_file;
    std::vector<double> execution_history;
    size_t max_history = 50;

public:
    Logger(const std::string &filename)
    {
        log_file.open(filename, std::ios::out);
        log_file << "JobID,ThreadID,SubmitTime,StartTime,EndTime,ExecDurationMS,QueueWaitMS,IsAnomaly\n";
    }

    ~Logger()
    {
        if (log_file.is_open())
            log_file.close();
    }

    void log(int job_id, int thread_id,
             std::chrono::high_resolution_clock::time_point submit_time,
             std::chrono::high_resolution_clock::time_point start_time,
             std::chrono::high_resolution_clock::time_point end_time)
    {
        using namespace std::chrono;

        std::lock_guard<std::mutex> lock(log_mutex);

        auto submit_ms = duration_cast<milliseconds>(submit_time.time_since_epoch()).count();
        auto start_ms = duration_cast<milliseconds>(start_time.time_since_epoch()).count();
        auto end_ms = duration_cast<milliseconds>(end_time.time_since_epoch()).count();

        auto exec_duration = end_ms - start_ms;
        auto queue_wait = start_ms - submit_ms;

        bool is_anomaly = detectAnomalyRealTime(exec_duration);

        execution_history.push_back(exec_duration);
        if (execution_history.size() > max_history)
        {
            execution_history.erase(execution_history.begin());
        }

        log_file << job_id << "," << thread_id << ","
                 << submit_ms << "," << start_ms << "," << end_ms << ","
                 << exec_duration << "," << queue_wait << ","
                 << (is_anomaly ? "1" : "0") << "\n";
        log_file.flush();

        if (is_anomaly)
        {
            std::cout << "🚨 REAL-TIME ANOMALY DETECTED: Job " << job_id
                      << " took " << exec_duration << "ms (Thread " << thread_id << ")\n";
        }
    }

private:
    bool detectAnomalyRealTime(double current_duration)
    {
        if (execution_history.size() < 10)
            return false;

        double mean = std::accumulate(execution_history.begin(), execution_history.end(), 0.0) / execution_history.size();

        double variance = 0.0;
        for (double duration : execution_history)
        {
            variance += (duration - mean) * (duration - mean);
        }
        variance /= execution_history.size();
        double std_dev = std::sqrt(variance); // std::sqrt now available

        double z_score = std::abs((current_duration - mean) / std_dev);

        return z_score > 2.0;
    }
};
