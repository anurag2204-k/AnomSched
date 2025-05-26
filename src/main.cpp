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

int main()
{
    Scheduler scheduler(4, "execution_log.csv");
    scheduler.start();

    std::cout << "Starting scheduler with intentional anomalies...\n";
    stressTestScheduler(scheduler, 100);

    std::this_thread::sleep_for(std::chrono::seconds(15)); // Longer wait
    scheduler.stop();
    std::cout << "Scheduler stopped.\n";

    return 0;
}
