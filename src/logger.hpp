#pragma once
#include <fstream>
#include <mutex>
#include <string>
#include <chrono>
#include <iomanip>

class Logger {
    std::mutex log_mutex;
    std::ofstream log_file;

public:
    Logger(const std::string& filename) {
        log_file.open(filename, std::ios::out);
        // Write CSV header
        log_file << "JobID,ThreadID,SubmitTime,StartTime,EndTime,ExecDurationMS,QueueWaitMS\n";
    }

    ~Logger() {
        if (log_file.is_open()) log_file.close();
    }

    void log(int job_id, int thread_id,
             std::chrono::high_resolution_clock::time_point submit_time,
             std::chrono::high_resolution_clock::time_point start_time,
             std::chrono::high_resolution_clock::time_point end_time) {
        using namespace std::chrono;

        std::lock_guard<std::mutex> lock(log_mutex);

        auto submit_ms = duration_cast<milliseconds>(submit_time.time_since_epoch()).count();
        auto start_ms = duration_cast<milliseconds>(start_time.time_since_epoch()).count();
        auto end_ms = duration_cast<milliseconds>(end_time.time_since_epoch()).count();
        auto exec_duration = duration_cast<milliseconds>(end_time - start_time).count();
        auto queue_wait = duration_cast<milliseconds>(start_time - submit_time).count();

        log_file << job_id << "," << thread_id << "," 
                 << submit_ms << "," << start_ms << "," << end_ms << ","
                 << exec_duration << "," << queue_wait << "\n";
        log_file.flush();
    }
};
