#include "scheduler.hpp"
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <random>

void stressTestScheduler(Scheduler &scheduler, int jobCount)
{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> normal_sleep(50, 150);
    std::uniform_int_distribution<> anomaly_sleep(300, 800); // Much longer
    std::uniform_real_distribution<> anomaly_chance(0.0, 1.0);

    for (int i = 0; i < jobCount; ++i)
    {
        scheduler.submitJob([i, &normal_sleep, &anomaly_sleep, &anomaly_chance, &gen]()
                            {
            int sleep_ms;
            bool is_anomaly = anomaly_chance(gen) < 0.15;  // 15% chance of anomaly
            
            if (is_anomaly) {
                sleep_ms = anomaly_sleep(gen);  // 300-800ms (anomalous)
                std::cout << "ANOMALY: Job " << i << " sleeping for " << sleep_ms << "ms\n";
            } else {
                sleep_ms = normal_sleep(gen);   // 50-150ms (normal)
            }
            
            std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms)); }, i % 10); // Add some priority variation
    }
}

void advancedStressTest(Scheduler &scheduler, int jobCount)
{
    std::random_device rd;
    std::mt19937 gen(rd());

    for (int i = 0; i < jobCount; ++i)
    {
        int anomaly_type = i % 20;

        scheduler.submitJob([i, anomaly_type]()
                            {
            switch (anomaly_type) {
                case 0: { // CPU spike anomaly - add braces
                    std::cout << "CPU SPIKE: Job " << i << "\n";
                    volatile long sum = 0;
                    for (int j = 0; j < 10000000; ++j) sum += j;
                    break;
                }
                    
                case 1: { // Memory allocation anomaly - add braces
                    std::cout << "MEMORY ANOMALY: Job " << i << "\n";
                    std::vector<int> big_vector(1000000, i);
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                    break;
                }
                    
                case 2: { // I/O simulation anomaly - add braces
                    std::cout << "IO ANOMALY: Job " << i << "\n";
                    std::this_thread::sleep_for(std::chrono::milliseconds(500));
                    break;
                }
                    
                case 3: { // Thread contention anomaly - add braces
                    std::cout << "CONTENTION ANOMALY: Job " << i << "\n";
                    static std::mutex contention_mutex;
                    std::lock_guard<std::mutex> lock(contention_mutex);
                    std::this_thread::sleep_for(std::chrono::milliseconds(200));
                    break;
                }
                    
                default: { // Normal job - add braces
                    int sleep_ms = 50 + (rand() % 100);
                    std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));
                    break;
                }
            } }, (i % 10) + 1);
    }
}

int main()
{
    Scheduler scheduler(4, "execution_log.csv");
    scheduler.start();

    std::cout << "Starting scheduler with intentional anomalies...\n";
    advancedStressTest(scheduler, 100);

    std::this_thread::sleep_for(std::chrono::seconds(15)); // Longer wait
    scheduler.stop();
    std::cout << "Scheduler stopped.\n";

    return 0;
}
