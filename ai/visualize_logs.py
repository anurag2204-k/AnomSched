import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class SchedulerAnalyzer:
    def __init__(self, csv_path='../build/execution_log.csv'):
        self.df = pd.read_csv(csv_path)
        self.prepare_data()
    
    def prepare_data(self):
        """Prepare and enrich the data for analysis"""
        # Convert to relative time
        self.df['StartTimeRel'] = self.df['StartTime'] - self.df['StartTime'].min()
        
        # Check if we have real-time anomaly detection
        if 'IsAnomaly' in self.df.columns:
            self.df['RealTimeAnomaly'] = self.df['IsAnomaly'].astype(bool)
        else:
            self.df['RealTimeAnomaly'] = False
            
        # Statistical anomaly detection (for comparison)
        self.detect_statistical_anomalies()
        
        # Performance metrics
        self.df['TotalTime'] = self.df['ExecDurationMS'] + self.df['QueueWaitMS']
        self.df['EfficiencyRatio'] = self.df['ExecDurationMS'] / self.df['TotalTime']
    
    def detect_statistical_anomalies(self):
        """Detect anomalies using statistical methods"""
        # Z-score method
        duration_mean = self.df['ExecDurationMS'].mean()
        duration_std = self.df['ExecDurationMS'].std()
        self.df['ZScore'] = (self.df['ExecDurationMS'] - duration_mean) / duration_std
        self.df['StatisticalAnomaly'] = self.df['ZScore'].abs() > 2
        
        # IQR method
        Q1 = self.df['ExecDurationMS'].quantile(0.25)
        Q3 = self.df['ExecDurationMS'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        self.df['IQRAnomaly'] = (self.df['ExecDurationMS'] < lower_bound) | \
                               (self.df['ExecDurationMS'] > upper_bound)
    
    def create_anomaly_comparison_plot(self):
        """Compare different anomaly detection methods"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Anomaly Detection Methods Comparison', fontsize=16)
        
        # 1. Timeline with real-time anomalies
        ax1 = axes[0, 0]
        normal = self.df[~self.df['RealTimeAnomaly']]
        anomaly = self.df[self.df['RealTimeAnomaly']]
        
        ax1.scatter(normal['StartTimeRel'], normal['ExecDurationMS'], 
                   c='blue', alpha=0.6, s=30, label=f'Normal ({len(normal)})')
        ax1.scatter(anomaly['StartTimeRel'], anomaly['ExecDurationMS'], 
                   c='red', s=50, label=f'Real-time Anomaly ({len(anomaly)})')
        ax1.set_title('Real-time Anomaly Detection')
        ax1.set_xlabel('Start Time (ms)')
        ax1.set_ylabel('Execution Duration (ms)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Statistical anomalies
        ax2 = axes[0, 1]
        normal_stat = self.df[~self.df['StatisticalAnomaly']]
        anomaly_stat = self.df[self.df['StatisticalAnomaly']]
        
        ax2.scatter(normal_stat['StartTimeRel'], normal_stat['ExecDurationMS'], 
                   c='blue', alpha=0.6, s=30, label=f'Normal ({len(normal_stat)})')
        ax2.scatter(anomaly_stat['StartTimeRel'], anomaly_stat['ExecDurationMS'], 
                   c='orange', s=50, label=f'Statistical Anomaly ({len(anomaly_stat)})')
        ax2.set_title('Statistical Anomaly Detection (Z-score)')
        ax2.set_xlabel('Start Time (ms)')
        ax2.set_ylabel('Execution Duration (ms)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Method comparison
        ax3 = axes[1, 0]
        detection_counts = [
            len(self.df[self.df['RealTimeAnomaly']]),
            len(self.df[self.df['StatisticalAnomaly']]),
            len(self.df[self.df['IQRAnomaly']]),
            len(self.df[self.df['RealTimeAnomaly'] & self.df['StatisticalAnomaly']])
        ]
        methods = ['Real-time', 'Statistical', 'IQR', 'Both Real-time\n& Statistical']
        bars = ax3.bar(methods, detection_counts, 
                      color=['red', 'orange', 'green', 'purple'])
        ax3.set_title('Anomaly Detection Method Comparison')
        ax3.set_ylabel('Anomalies Detected')
        for bar, count in zip(bars, detection_counts):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    str(count), ha='center', va='bottom')
        
        # 4. Execution duration distribution
        ax4 = axes[1, 1]
        ax4.hist([normal['ExecDurationMS'], anomaly['ExecDurationMS']], 
                bins=30, alpha=0.7, label=['Normal', 'Anomaly'], 
                color=['blue', 'red'])
        ax4.axvline(self.df['ExecDurationMS'].mean(), color='black', 
                   linestyle='--', label='Mean')
        ax4.axvline(self.df['ExecDurationMS'].mean() + 2*self.df['ExecDurationMS'].std(), 
                   color='orange', linestyle='--', label='2σ threshold')
        ax4.set_title('Duration Distribution')
        ax4.set_xlabel('Execution Duration (ms)')
        ax4.set_ylabel('Frequency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def print_anomaly_summary(self):
        """Print detailed anomaly analysis"""
        total_jobs = len(self.df)
        real_time_anomalies = self.df['RealTimeAnomaly'].sum()
        statistical_anomalies = self.df['StatisticalAnomaly'].sum()
        
        print("=" * 60)
        print("ANOMALY DETECTION SUMMARY")
        print("=" * 60)
        print(f"Total Jobs Processed: {total_jobs}")
        print(f"Real-time Anomalies: {real_time_anomalies} ({real_time_anomalies/total_jobs*100:.1f}%)")
        print(f"Statistical Anomalies: {statistical_anomalies} ({statistical_anomalies/total_jobs*100:.1f}%)")
        
        if real_time_anomalies > 0:
            anomaly_jobs = self.df[self.df['RealTimeAnomaly']]
            print(f"\nAnomaly Details:")
            print(f"  Average Duration: {anomaly_jobs['ExecDurationMS'].mean():.1f}ms")
            print(f"  Max Duration: {anomaly_jobs['ExecDurationMS'].max()}ms")
            print(f"  Anomaly Jobs: {list(anomaly_jobs['JobID'].values)}")

# Usage
if __name__ == "__main__":
    analyzer = SchedulerAnalyzer()
    analyzer.print_anomaly_summary()
    
    # Create anomaly comparison plots
    fig = analyzer.create_anomaly_comparison_plot()
    plt.show()
