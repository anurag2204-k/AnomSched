import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class SchedulerAnalyzer:
    def __init__(self, csv_path='../build/execution_log.csv'):
        self.df = pd.read_csv(csv_path)
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare and enrich the data for analysis"""
        # Convert to relative time
        self.df['StartTimeRel'] = self.df['StartTime'] - self.df['StartTime'].min()
        self.df['EndTimeRel'] = self.df['EndTime'] - self.df['StartTime'].min()
        
        # Calculate additional metrics
        self.df['TotalTime'] = self.df['ExecDurationMS'] + self.df['QueueWaitMS']
        self.df['EfficiencyRatio'] = self.df['ExecDurationMS'] / self.df['TotalTime']
        
        # Detect anomalies using multiple methods
        self.detect_anomalies()
        
        # Calculate throughput over time
        self.calculate_throughput()
    
    def detect_anomalies(self):
        """Detect anomalies using multiple statistical methods"""
        # Z-score method
        duration_mean = self.df['ExecDurationMS'].mean()
        duration_std = self.df['ExecDurationMS'].std()
        self.df['ZScore'] = (self.df['ExecDurationMS'] - duration_mean) / duration_std
        self.df['ZScoreAnomaly'] = self.df['ZScore'].abs() > 2
        
        # IQR method
        Q1 = self.df['ExecDurationMS'].quantile(0.25)
        Q3 = self.df['ExecDurationMS'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        self.df['IQRAnomaly'] = (self.df['ExecDurationMS'] < lower_bound) | (self.df['ExecDurationMS'] > upper_bound)
        
        # Queue wait anomalies
        wait_mean = self.df['QueueWaitMS'].mean()
        wait_std = self.df['QueueWaitMS'].std()
        self.df['WaitAnomaly'] = (self.df['QueueWaitMS'] - wait_mean).abs() > 2 * wait_std
        
        # Combined anomaly flag
        self.df['IsAnomaly'] = self.df['ZScoreAnomaly'] | self.df['IQRAnomaly'] | self.df['WaitAnomaly']
    
    def calculate_throughput(self):
        """Calculate jobs completed per time window"""
        time_windows = np.arange(0, self.df['EndTimeRel'].max(), 500)  # 500ms windows
        throughput = []
        
        for i in range(len(time_windows) - 1):
            start_window = time_windows[i]
            end_window = time_windows[i + 1]
            jobs_completed = len(self.df[(self.df['EndTimeRel'] >= start_window) & 
                                       (self.df['EndTimeRel'] < end_window)])
            throughput.append(jobs_completed)
        
        self.throughput_df = pd.DataFrame({
            'TimeWindow': time_windows[:-1],
            'JobsCompleted': throughput
        })
    
    def create_interactive_dashboard(self):
        """Create an interactive Plotly dashboard"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Job Timeline', 'Execution Duration Distribution', 
                          'Thread Workload', 'Queue Wait vs Execution Time',
                          'Throughput Over Time', 'Anomaly Detection'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Job Timeline (Gantt-like)
        colors = ['red' if anomaly else 'blue' for anomaly in self.df['IsAnomaly']]
        fig.add_trace(
            go.Scatter(x=self.df['StartTimeRel'], y=self.df['JobID'],
                      mode='markers', marker=dict(color=colors, size=8),
                      name='Job Start', showlegend=False),
            row=1, col=1
        )
        
        # 2. Execution Duration Distribution
        fig.add_trace(
            go.Histogram(x=self.df['ExecDurationMS'], nbinsx=20, 
                        name='Duration Distribution', showlegend=False),
            row=1, col=2
        )
        
        # 3. Thread Workload
        for thread_id in sorted(self.df['ThreadID'].unique()):
            thread_data = self.df[self.df['ThreadID'] == thread_id]
            fig.add_trace(
                go.Scatter(x=thread_data['StartTimeRel'], y=thread_data['ExecDurationMS'],
                          mode='lines+markers', name=f'Thread {thread_id}'),
                row=2, col=1
            )
        
        # 4. Queue Wait vs Execution Time
        fig.add_trace(
            go.Scatter(x=self.df['QueueWaitMS'], y=self.df['ExecDurationMS'],
                      mode='markers', 
                      marker=dict(color=self.df['IsAnomaly'], 
                                colorscale='RdYlBu', size=8),
                      name='Jobs', showlegend=False),
            row=2, col=2
        )
        
        # 5. Throughput Over Time
        fig.add_trace(
            go.Scatter(x=self.throughput_df['TimeWindow'], 
                      y=self.throughput_df['JobsCompleted'],
                      mode='lines+markers', name='Throughput', showlegend=False),
            row=3, col=1
        )
        
        # 6. Anomaly Detection
        normal_jobs = self.df[~self.df['IsAnomaly']]
        anomaly_jobs = self.df[self.df['IsAnomaly']]
        
        fig.add_trace(
            go.Scatter(x=normal_jobs['StartTimeRel'], y=normal_jobs['ExecDurationMS'],
                      mode='markers', marker=dict(color='blue', size=6),
                      name='Normal', opacity=0.6),
            row=3, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=anomaly_jobs['StartTimeRel'], y=anomaly_jobs['ExecDurationMS'],
                      mode='markers', marker=dict(color='red', size=10),
                      name='Anomaly'),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(height=1200, title_text="Scheduler Performance Dashboard")
        fig.update_xaxes(title_text="Time (ms)", row=3, col=1)
        fig.update_xaxes(title_text="Time (ms)", row=3, col=2)
        fig.update_yaxes(title_text="Jobs/500ms", row=3, col=1)
        fig.update_yaxes(title_text="Duration (ms)", row=3, col=2)
        
        return fig
    
    def create_static_analysis(self):
        """Create comprehensive static analysis plots"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))
        fig.suptitle('Comprehensive Scheduler Analysis', fontsize=16, fontweight='bold')
        
        # 1. Timeline with anomalies
        ax1 = axes[0, 0]
        normal = self.df[~self.df['IsAnomaly']]
        anomaly = self.df[self.df['IsAnomaly']]
        ax1.scatter(normal['StartTimeRel'], normal['ExecDurationMS'], 
                   c='blue', alpha=0.6, s=30, label=f'Normal ({len(normal)})')
        ax1.scatter(anomaly['StartTimeRel'], anomaly['ExecDurationMS'], 
                   c='red', s=50, label=f'Anomaly ({len(anomaly)})')
        ax1.set_xlabel('Start Time (ms)')
        ax1.set_ylabel('Execution Duration (ms)')
        ax1.set_title('Job Execution Timeline')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Thread utilization heatmap
        ax2 = axes[0, 1]
        thread_perf = self.df.groupby(['ThreadID', pd.cut(self.df['StartTimeRel'], bins=20)]).size().unstack(fill_value=0)
        sns.heatmap(thread_perf, ax=ax2, cmap='YlOrRd', cbar_kws={'label': 'Jobs'})
        ax2.set_title('Thread Utilization Heatmap')
        ax2.set_xlabel('Time Bins')
        ax2.set_ylabel('Thread ID')
        
        # 3. Distribution comparison
        ax3 = axes[0, 2]
        ax3.hist([normal['ExecDurationMS'], anomaly['ExecDurationMS']], 
                bins=25, alpha=0.7, label=['Normal', 'Anomaly'], color=['blue', 'red'])
        ax3.set_xlabel('Execution Duration (ms)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Duration Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Queue wait analysis
        ax4 = axes[1, 0]
        ax4.scatter(self.df['QueueWaitMS'], self.df['ExecDurationMS'], 
                   c=self.df['ThreadID'], cmap='tab10', alpha=0.7)
        ax4.set_xlabel('Queue Wait Time (ms)')
        ax4.set_ylabel('Execution Duration (ms)')
        ax4.set_title('Queue Wait vs Execution Time')
        ax4.grid(True, alpha=0.3)
        
        # 5. Efficiency over time
        ax5 = axes[1, 1]
        ax5.plot(self.df['StartTimeRel'], self.df['EfficiencyRatio'], 'o-', alpha=0.7)
        ax5.set_xlabel('Start Time (ms)')
        ax5.set_ylabel('Efficiency Ratio')
        ax5.set_title('Execution Efficiency Over Time')
        ax5.grid(True, alpha=0.3)
        
        # 6. Throughput
        ax6 = axes[1, 2]
        ax6.plot(self.throughput_df['TimeWindow'], self.throughput_df['JobsCompleted'], 'o-', color='green')
        ax6.set_xlabel('Time Window (ms)')
        ax6.set_ylabel('Jobs Completed')
        ax6.set_title('System Throughput')
        ax6.grid(True, alpha=0.3)
        
        # 7. Thread performance comparison
        ax7 = axes[2, 0]
        thread_stats = self.df.groupby('ThreadID')['ExecDurationMS'].agg(['mean', 'std', 'count'])
        thread_stats.plot(kind='bar', ax=ax7, rot=0)
        ax7.set_title('Thread Performance Statistics')
        ax7.set_xlabel('Thread ID')
        ax7.legend(['Mean Duration', 'Std Dev', 'Job Count'])
        
        # 8. Anomaly detection methods comparison
        ax8 = axes[2, 1]
        anomaly_counts = [
            self.df['ZScoreAnomaly'].sum(),
            self.df['IQRAnomaly'].sum(),
            self.df['WaitAnomaly'].sum(),
            self.df['IsAnomaly'].sum()
        ]
        methods = ['Z-Score', 'IQR', 'Wait Time', 'Combined']
        bars = ax8.bar(methods, anomaly_counts, color=['blue', 'orange', 'green', 'red'])
        ax8.set_title('Anomaly Detection Methods')
        ax8.set_ylabel('Anomalies Found')
        for bar, count in zip(bars, anomaly_counts):
            ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(count), ha='center', va='bottom')
        
        # 9. Job completion rate
        ax9 = axes[2, 2]
        completion_times = np.sort(self.df['EndTimeRel'])
        cumulative_jobs = np.arange(1, len(completion_times) + 1)
        ax9.plot(completion_times, cumulative_jobs, 'g-', linewidth=2)
        ax9.set_xlabel('Time (ms)')
        ax9.set_ylabel('Cumulative Jobs Completed')
        ax9.set_title('Job Completion Rate')
        ax9.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def print_summary_stats(self):
        """Print comprehensive summary statistics"""
        print("=" * 60)
        print("SCHEDULER PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        print(f"Total Jobs: {len(self.df)}")
        print(f"Total Runtime: {self.df['EndTimeRel'].max():.0f} ms")
        print(f"Anomalies Detected: {self.df['IsAnomaly'].sum()} ({self.df['IsAnomaly'].mean()*100:.1f}%)")
        
        print("\n--- Execution Duration Stats ---")
        print(f"Mean: {self.df['ExecDurationMS'].mean():.1f} ms")
        print(f"Median: {self.df['ExecDurationMS'].median():.1f} ms")
        print(f"Std Dev: {self.df['ExecDurationMS'].std():.1f} ms")
        print(f"Min: {self.df['ExecDurationMS'].min()} ms")
        print(f"Max: {self.df['ExecDurationMS'].max()} ms")
        
        print("\n--- Queue Wait Stats ---")
        print(f"Mean Wait: {self.df['QueueWaitMS'].mean():.1f} ms")
        print(f"Max Wait: {self.df['QueueWaitMS'].max()} ms")
        print(f"Jobs with >1s wait: {(self.df['QueueWaitMS'] > 1000).sum()}")
        
        print("\n--- Thread Performance ---")
        thread_stats = self.df.groupby('ThreadID').agg({
            'ExecDurationMS': ['count', 'mean'],
            'QueueWaitMS': 'mean'
        }).round(1)
        print(thread_stats)
        
        print("\n--- System Efficiency ---")
        avg_efficiency = self.df['EfficiencyRatio'].mean()
        print(f"Average Efficiency: {avg_efficiency:.3f}")
        print(f"Peak Throughput: {self.throughput_df['JobsCompleted'].max()} jobs/500ms")

# Usage
if __name__ == "__main__":
    analyzer = SchedulerAnalyzer()
    
    # Print summary
    analyzer.print_summary_stats()
    
    # Create static plots
    static_fig = analyzer.create_static_analysis()
    plt.show()
    
    # Create interactive dashboard (requires plotly)
    try:
        interactive_fig = analyzer.create_interactive_dashboard()
        interactive_fig.show()
    except ImportError:
        print("\nInstall plotly for interactive dashboard: pip install plotly")
