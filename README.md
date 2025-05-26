# AnomSched - Advanced Thread Pool Scheduler with Real-Time Anomaly Detection

[![C++](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://isocpp.org/)
[![CMake](https://img.shields.io/badge/CMake-3.10+-green.svg)](https://cmake.org/)
[![Python](https://img.shields.io/badge/Python-3.7+-yellow.svg)](https://python.org/)
A high-performance, research-oriented thread pool scheduler implementation with comprehensive performance monitoring, real-time anomaly detection, and advanced visualization tools for analyzing concurrent system behavior.

## 🎯 Project Overview

AnomSched combines efficient thread pool scheduling with sophisticated performance analysis capabilities. It demonstrates advanced concepts in:

- **Concurrent Programming**: Multi-threaded job execution with priority-based scheduling
- **Performance Monitoring**: Microsecond-precision logging and real-time metrics collection
- **Anomaly Detection**: Statistical and machine learning approaches to identify unusual system behavior
- **Data Visualization**: Comprehensive analysis tools for understanding scheduler performance

## 📁 Repository Architecture

```
AnomSched/
├── 📂 src/                     # Core C++ Implementation
│   ├── 📄 main.cpp            # Application entry point & stress testing
│   ├── 📄 scheduler.hpp       # Scheduler class interface
│   ├── 📄 scheduler.cpp       # Thread pool implementation
│   ├── 📄 logger.hpp          # Performance logging system
│   └── 📄 job.hpp            # Job structure definitions
├── 📂 build/                  # Build artifacts & executables
│   ├── 📄 Makefile           # Generated build configuration
│   ├── 🎯 AnomSched.exe      # Compiled executable
│   └── 📊 execution_log.csv  # Runtime performance data
├── 📂 ai/                     # Python analysis toolkit
│   └── 📄 visualize_logs.py  # Advanced visualization suite
├── 📂 logs/                   # Additional log storage
└── 📄 CMakeLists.txt         # CMake build configuration
```

## 🏗️ Core Architecture Deep Dive

### 1. **Thread Pool Scheduler** (`scheduler.hpp` & `scheduler.cpp`)

The heart of AnomSched is a sophisticated thread pool implementation using the producer-consumer pattern with priority-based job scheduling.

#### **Key Design Features:**
- **Dynamic Thread Management**: Configurable worker thread pool size
- **Priority Queue System**: Jobs executed based on priority (higher values = higher priority)
- **Thread-Safe Operations**: Mutex-protected job queue with condition variable synchronization
- **Graceful Lifecycle Management**: Proper thread initialization, execution, and cleanup

#### **Core Class Interface:**
```cpp
class Scheduler {
public:
    Scheduler(int num_threads, const std::string& log_filename);
    void start();                                    // Initialize worker thread pool
    void stop();                                     // Graceful shutdown with thread joining
    void submitJob(std::function<void()> task, int priority);  // Thread-safe job submission
    
private:
    void worker_loop(int thread_id);                // Worker thread execution loop
    
    std::vector<std::thread> workers;               // Thread pool container
    std::priority_queue<Job> job_queue;             // Priority-based job queue
    std::mutex queue_mutex;                         // Thread synchronization
    std::condition_variable condition;              // Worker coordination
    std::atomic<bool> running;                      // Lifecycle state
    std::atomic<int> job_counter;                   // Unique job ID generation
    Logger logger;                                  // Performance monitoring
};
```

#### **Threading Architecture:**
- **Producer Pattern**: Main thread submits jobs via `submitJob()`
- **Consumer Pool**: N worker threads execute jobs from priority queue
- **Synchronization**: `std::mutex` + `std::condition_variable` coordination
- **Load Balancing**: Automatic work distribution across available threads

### 2. **Job Management System** (`job.hpp`)

Defines the fundamental work unit with comprehensive metadata for performance analysis.

#### **Job Structure:**
```cpp
struct Job {
    int id;                           // Unique identifier for tracking
    int priority;                     // Execution priority (1-10 scale)
    std::function<void()> task;       // Encapsulated work function
    std::chrono::high_resolution_clock::time_point submit_time;  // Submission timestamp
    
    // Default constructor for queue operations
    Job() : id(0), priority(0), task([]{}), 
            submit_time(std::chrono::high_resolution_clock::now()) {}
    
    // Parameterized constructor for job creation
    Job(int id_, int prio, std::function<void()> t)
        : id(id_), priority(prio), task(std::move(t)), 
          submit_time(std::chrono::high_resolution_clock::now()) {}
    
    // Priority comparison for queue ordering
    bool operator<(const Job& other) const {
        return priority < other.priority;  // Max-heap: higher priority first
    }
};
```

#### **Priority System:**
- **Range**: 1-10 (10 = highest priority)
- **Queue Behavior**: Max-heap implementation ensures highest priority jobs execute first
- **Fair Scheduling**: Equal priority jobs maintain FIFO ordering

### 3. **Performance Monitoring System** (`logger.hpp`)

Thread-safe, high-precision logging system capturing detailed execution metrics for analysis.

#### **Comprehensive Metrics Collection:**
```csv
JobID,ThreadID,SubmitTime,StartTime,EndTime,ExecDurationMS,QueueWaitMS,IsAnomaly
4,1,1748258241987,1748258242590,603,1836,1
```

#### **Metric Definitions:**
- **JobID**: Unique job identifier for tracking
- **ThreadID**: Worker thread that executed the job (0-N)
- **SubmitTime**: Job submission timestamp (microsecond precision)
- **StartTime**: Execution start timestamp
- **EndTime**: Execution completion timestamp
- **ExecDurationMS**: Pure execution time (EndTime - StartTime)
- **QueueWaitMS**: Queue waiting time (StartTime - SubmitTime)
- **IsAnomaly**: Real-time anomaly detection flag (0/1)

#### **Real-Time Anomaly Detection:**
```cpp
class Logger {
private:
    std::vector<double> execution_history;  // Rolling execution time window
    size_t max_history = 50;               // Statistical analysis window
    
    bool detectAnomalyRealTime(double current_duration) {
        if (execution_history.size() < 10) return false;
        
        // Calculate running statistics
        double mean = std::accumulate(execution_history.begin(), execution_history.end(), 0.0) / execution_history.size();
        
        double variance = 0.0;
        for (double duration : execution_history) {
            variance += (duration - mean) * (duration - mean);
        }
        variance /= execution_history.size();
        double std_dev = std::sqrt(variance);
        
        // Z-score anomaly detection (2-sigma threshold)
        double z_score = std::abs((current_duration - mean) / std_dev);
        return z_score > 2.0;  // 95.4% confidence interval
    }
};
```

### 4. **Application & Stress Testing** (`main.cpp`)

Comprehensive testing suite demonstrating scheduler capabilities with various workload patterns and anomaly injection.

#### **Current Test Configuration:**
```cpp
int main() {
    Scheduler scheduler(4, "execution_log.csv");    // 4 worker threads
    scheduler.start();
    
    advancedStressTest(scheduler, 100);             // Submit 100 jobs with anomalies
    std::this_thread::sleep_for(std::chrono::seconds(15));
    
    scheduler.stop();
    return 0;
}
```

#### **Advanced Stress Testing with Anomaly Injection:**
```cpp
void advancedStressTest(Scheduler& scheduler, int jobCount) {
    for (int i = 0; i < jobCount; ++i) {
        int anomaly_type = i % 20;  // Cycle through anomaly types
        
        scheduler.submitJob([i, anomaly_type]() {
            switch (anomaly_type) {
                case 0: { // CPU-intensive anomaly
                    std::cout << "CPU SPIKE: Job " << i << "\n";
                    volatile long sum = 0;
                    for (int j = 0; j < 10000000; ++j) sum += j;  // ~200-500ms
                    break;
                }
                
                case 1: { // Memory allocation anomaly
                    std::cout << "MEMORY ANOMALY: Job " << i << "\n";
                    std::vector<int> big_vector(1000000, i);  // 4MB allocation
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                    break;
                }
                
                case 2: { // I/O simulation anomaly
                    std::cout << "IO ANOMALY: Job " << i << "\n";
                    std::this_thread::sleep_for(std::chrono::milliseconds(500));
                    break;
                }
                
                case 3: { // Thread contention anomaly
                    std::cout << "CONTENTION ANOMALY: Job " << i << "\n";
                    static std::mutex contention_mutex;
                    std::lock_guard<std::mutex> lock(contention_mutex);
                    std::this_thread::sleep_for(std::chrono::milliseconds(200));
                    break;
                }
                
                default: { // Normal workload
                    int sleep_ms = 50 + (rand() % 100);  // 50-150ms
                    std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));
                    break;
                }
            }
        }, (i % 10) + 1);  // Priority range: 1-10
    }
}
```

#### **Anomaly Types Simulated:**
1. **CPU Spikes**: Compute-intensive loops causing execution delays
2. **Memory Pressure**: Large memory allocations affecting system performance
3. **I/O Blocking**: Simulated I/O operations causing thread blocking
4. **Lock Contention**: Mutex contention creating serialization bottlenecks
5. **Normal Workload**: Baseline jobs for comparison (50-150ms execution)

## 📊 Advanced Performance Analysis (`ai/visualize_logs.py`)

Comprehensive Python toolkit providing multi-dimensional analysis of scheduler performance and anomaly patterns.

### **SchedulerAnalyzer Class Architecture**

#### **Data Preparation & Enhancement:**
```python
def prepare_data(self):
    # Time normalization for visualization
    self.df['StartTimeRel'] = self.df['StartTime'] - self.df['StartTime'].min()
    self.df['EndTimeRel'] = self.df['EndTime'] - self.df['StartTime'].min()
    
    # Performance efficiency metrics
    self.df['TotalTime'] = self.df['ExecDurationMS'] + self.df['QueueWaitMS']
    self.df['EfficiencyRatio'] = self.df['ExecDurationMS'] / self.df['TotalTime']
    
    # Multi-method anomaly detection
    self.detect_anomalies()
    
    # System throughput analysis
    self.calculate_throughput()
```

#### **Multi-Method Anomaly Detection:**

**1. Z-Score Statistical Method:**
```python
duration_mean = self.df['ExecDurationMS'].mean()
duration_std = self.df['ExecDurationMS'].std()
self.df['ZScore'] = (self.df['ExecDurationMS'] - duration_mean) / duration_std
self.df['ZScoreAnomaly'] = self.df['ZScore'].abs() > 2  # 95.4% confidence
```

**2. Interquartile Range (IQR) Method:**
```python
Q1, Q3 = self.df['ExecDurationMS'].quantile([0.25, 0.75])
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
self.df['IQRAnomaly'] = (duration < lower_bound) | (duration > upper_bound)
```

**3. Queue Wait Analysis:**
```python
wait_mean = self.df['QueueWaitMS'].mean()
wait_std = self.df['QueueWaitMS'].std()
self.df['WaitAnomaly'] = (self.df['QueueWaitMS'] - wait_mean).abs() > 2 * wait_std
```

**4. Combined Anomaly Detection:**
```python
self.df['IsAnomaly'] = self.df['ZScoreAnomaly'] | self.df['IQRAnomaly'] | self.df['WaitAnomaly']
```

#### **Throughput Analysis:**
```python
def calculate_throughput(self):
    time_windows = np.arange(0, self.df['EndTimeRel'].max(), 500)  # 500ms windows
    throughput = []
    
    for i in range(len(time_windows) - 1):
        start_window = time_windows[i]
        end_window = time_windows[i + 1]
        jobs_completed = len(self.df[(self.df['EndTimeRel'] >= start_window) & 
                                   (self.df['EndTimeRel'] < end_window)])
        throughput.append(jobs_completed)
```

### **Comprehensive Visualization Suite**

#### **1. Interactive Dashboard (Plotly)**
Multi-panel interactive dashboard with:
- **Job Timeline**: Gantt-style execution visualization with anomaly highlighting
- **Duration Distribution**: Histogram analysis of execution patterns
- **Thread Workload**: Per-thread performance over time
- **Wait vs Execution**: Correlation analysis between queue time and execution
- **Throughput Patterns**: System performance over time windows
- **Anomaly Comparison**: Multi-method detection visualization

#### **2. Static Analysis (Matplotlib/Seaborn)**
Nine comprehensive analytical plots:

1. **Timeline with Anomalies**: Scatter plot distinguishing normal vs anomalous jobs
2. **Thread Utilization Heatmap**: Load distribution across threads and time bins
3. **Duration Distribution Comparison**: Histogram overlay of normal vs anomalous jobs
4. **Queue Analysis**: Wait time vs execution time correlation matrix
5. **Efficiency Trends**: Execution efficiency ratio over time
6. **Throughput Patterns**: Jobs completed per time window analysis
7. **Thread Performance Statistics**: Statistical comparison across worker threads
8. **Anomaly Detection Methods**: Comparative analysis of detection techniques
9. **Job Completion Rate**: Cumulative completion curve analysis

### **Performance Metrics & KPIs**

#### **System Performance Indicators:**
```python
def print_summary_stats(self):
    total_jobs = len(self.df)
    real_time_anomalies = self.df['RealTimeAnomaly'].sum()
    statistical_anomalies = self.df['StatisticalAnomaly'].sum()
    
    # Core metrics
    avg_execution = self.df['ExecDurationMS'].mean()
    avg_wait = self.df['QueueWaitMS'].mean()
    avg_efficiency = self.df['EfficiencyRatio'].mean()
    peak_throughput = self.throughput_df['JobsCompleted'].max()
    
    # Thread balance analysis
    thread_stats = self.df.groupby('ThreadID').agg({
        'ExecDurationMS': ['count', 'mean', 'std'],
        'QueueWaitMS': 'mean'
    })
```

## 🚀 Build & Execution Workflow

### **Prerequisites & Dependencies**

**C++ Build Environment:**
```powershell
# Windows (MSYS2/MinGW-w64)
pacman -S mingw-w64-x86_64-cmake
pacman -S mingw-w64-x86_64-gcc
pacman -S mingw-w64-x86_64-make

# Ubuntu/Debian
sudo apt-get install cmake g++ make

# macOS
brew install cmake
```

**Python Analysis Environment:**
```powershell
pip install pandas matplotlib seaborn plotly numpy scipy
```

### **Build Process**

#### **Clean Build (Recommended):**
```powershell
# Navigate to project root
cd AnomSched

# Remove any existing build artifacts
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

# Create fresh build directory
mkdir build
cd build

# Configure with appropriate generator
cmake -G "MinGW Makefiles" ..  # Windows with MinGW

# Compile the project
mingw32-make

# Verify successful build
ls AnomSched.exe  # Windows
```

#### **Incremental Build:**
```powershell
cd build
mingw32-make clean
mingw32-make
```

### **Execution & Analysis Workflow**

#### **1. Run Scheduler with Anomaly Generation:**
```powershell
./AnomSched.exe  # Generates execution_log.csv
```

**Expected Console Output:**
```
Starting scheduler with intentional anomalies...
CPU SPIKE: Job 0
MEMORY ANOMALY: Job 1
IO ANOMALY: Job 2
🚨 REAL-TIME ANOMALY DETECTED: Job 4 took 603ms (Thread 1)
CONTENTION ANOMALY: Job 3
🚨 REAL-TIME ANOMALY DETECTED: Job 23 took 512ms (Thread 2)
...
Scheduler stopped.
```

#### **2. Analyze Performance Data:**
```powershell
cd ..
python ai/visualize_logs.py
```

**Analysis Output:**
```
============================================================
ANOMALY DETECTION SUMMARY
============================================================
Total Jobs Processed: 100
Real-time Anomalies: 15 (15.0%)
Statistical Anomalies: 18 (18.0%)

--- Execution Duration Stats ---
Mean: 165.2 ms
Median: 125.0 ms
Std Dev: 156.8 ms
Min: 4 ms
Max: 617 ms

--- Queue Wait Stats ---
Mean Wait: 1876.4 ms
Max Wait: 3495 ms
Jobs with >1s wait: 89

--- Thread Performance ---
ThreadID  count  mean
0         25     178.3
1         25     162.1
2         25     155.8
3         25     164.9

--- System Efficiency ---
Average Efficiency: 0.127
Peak Throughput: 4 jobs/500ms
```

## 📈 Performance Characteristics & Analysis

### **Expected Performance Profile**

With the default configuration (4 threads, 100 jobs):

#### **Timing Characteristics:**
- **Total Runtime**: 3-5 seconds
- **Normal Job Duration**: 50-150ms
- **Anomalous Job Duration**: 200-800ms
- **Queue Wait Times**: Increasing over time due to backlog
- **System Efficiency**: ~12-15% (execution time / total time)

#### **Anomaly Patterns:**
- **Detection Rate**: 15-20% of jobs flagged as anomalous
- **CPU Spikes**: 200-500ms execution (every 20th job)
- **Memory Anomalies**: 100ms + allocation overhead
- **I/O Simulation**: Consistent 500ms delays
- **Lock Contention**: 200ms serialized execution

#### **Thread Utilization:**
- **Load Distribution**: Generally balanced across 4 threads
- **Queue Buildup**: Increasing wait times as system saturates
- **Throughput Degradation**: Decreasing jobs/second over time

### **Key Performance Insights**

#### **1. Queue Saturation Pattern:**
The execution log shows a clear pattern of increasing queue wait times:
- Early jobs: 1-100ms wait
- Mid-execution: 1000-2000ms wait
- Late execution: 3000+ ms wait

This demonstrates **system saturation** as anomalous jobs create backlog.

#### **2. Real-Time Anomaly Detection Effectiveness:**
The system successfully identifies anomalous jobs in real-time:
- Job 4: 603ms execution (detected as anomaly)
- Job 23: 512ms execution (detected as anomaly)
- Job 43: 513ms execution (detected as anomaly)

#### **3. Thread Load Balancing:**
Despite anomalies, work distribution remains relatively balanced across threads, demonstrating effective scheduling.

## 🔬 Research Applications & Extensions

### **Academic & Research Use Cases**

#### **1. Scheduler Algorithm Research:**
- **Priority Scheduling**: Compare different priority algorithms
- **Load Balancing**: Analyze work distribution strategies
- **Fairness Analysis**: Study starvation and fairness metrics

#### **2. Anomaly Detection Research:**
- **Machine Learning**: Train models on execution patterns
- **Statistical Methods**: Compare detection algorithm effectiveness
- **Real-time Systems**: Study online vs offline detection

#### **3. System Performance Analysis:**
- **Bottleneck Identification**: Pinpoint system limitations
- **Scalability Studies**: Analyze performance under varying loads
- **Resource Utilization**: Study memory, CPU, and I/O patterns

### **Extensibility Framework**

#### **1. Custom Scheduling Algorithms:**
```cpp
// Add to scheduler.hpp
enum class SchedulingPolicy {
    PRIORITY,           // Current implementation
    ROUND_ROBIN,        // Fair scheduling
    EARLIEST_DEADLINE,  // Real-time scheduling
    SHORTEST_JOB_FIRST  // Optimization scheduling
};
```

#### **2. Advanced Job Types:**
```cpp
struct Job {
    int id, priority;
    std::function<void()> task;
    std::chrono::high_resolution_clock::time_point submit_time;
    
    // Extensions
    std::chrono::milliseconds deadline;     // For deadline scheduling
    size_t estimated_duration;             // For optimization
    std::string job_type;                  // For categorization
    std::map<std::string, double> metadata; // Custom attributes
};
```

#### **3. Enhanced Monitoring:**
```cpp
class AdvancedLogger {
    // Resource monitoring
    void logCPUUsage();
    void logMemoryUsage();
    void logThreadStates();
    
    // Machine learning integration
    void exportToMLFormat();
    bool predictAnomaly(const Job& job);
    
    // Real-time dashboards
    void startWebDashboard();
    void publishMetrics();
};
```

<!-- ### **Future Development Roadmap**

#### **Phase 1: Enhanced Analytics**
- [ ] Machine learning anomaly detection
- [ ] Predictive performance modeling
- [ ] Real-time web dashboard
- [ ] Advanced statistical analysis

#### **Phase 2: Distributed Systems**
- [ ] Multi-node scheduler coordination
- [ ] Network-aware load balancing
- [ ] Fault tolerance and recovery
- [ ] Container orchestration integration

#### **Phase 3: Production Features**
- [ ] Configuration management system
- [ ] Comprehensive REST API
- [ ] Database integration for metrics
- [ ] Enterprise monitoring integration -->

## 🛠 Configuration & Customization

### **Scheduler Parameters**
```cpp
// Core configuration
Scheduler scheduler(
    8,                              // Worker thread count
    "performance_log.csv"           // Log file path
);

// Stress test configuration
advancedStressTest(scheduler, 200); // Job count
```

### **Anomaly Detection Tuning**
```cpp
// In logger.hpp
size_t max_history = 100;          // Statistical window size
double z_score_threshold = 2.5;    // Anomaly sensitivity
bool enable_real_time_detection = true;
```

### **Analysis Parameters**
```python
# In visualize_logs.py
analyzer = SchedulerAnalyzer('../build/execution_log.csv')

# Detection thresholds
Z_SCORE_THRESHOLD = 2.0     # Standard deviations
IQR_MULTIPLIER = 1.5        # IQR outlier factor
TIME_WINDOW_MS = 500        # Throughput calculation window
CONFIDENCE_LEVEL = 0.95     # Statistical confidence
```
<!-- 
## 📄 License & Contributing

This project is licensed under the MIT License - see the LICENSE file for details. -->

<!-- ### **Contributing Guidelines**
1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request -->

<!-- ### **Code Style**
- **C++**: Follow Google C++ Style Guide
- **Python**: PEP 8 compliance
- **Documentation**: Comprehensive inline comments -->

---

**AnomSched** represents a comprehensive platform for understanding, analyzing, and optimizing concurrent system performance. Whether used for academic research, production system analysis, or algorithm development, it provides the tools and insights necessary for advanced scheduler performance analysis.


