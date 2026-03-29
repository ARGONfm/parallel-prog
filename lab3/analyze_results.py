import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

plt.style.use('ggplot')
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (12, 8)

RESULTS_FILE = "experiment_results.csv"
PLOTS_DIR = Path("plots")

def ensure_plots_dir():
    PLOTS_DIR.mkdir(exist_ok=True)

def load_and_aggregate():
    print("Loading results...")
    if not Path(RESULTS_FILE).exists():
        print(f"Error: {RESULTS_FILE} not found!")
        sys.exit(1)
    
    df = pd.read_csv(RESULTS_FILE)
    df_mean = df.groupby(['N', 'processes'])['time_seconds'].mean().reset_index()
    return df_mean

def print_summary_table(df):
    print("\n" + "=" * 80)
    print("SUMMARY TABLE (MPI)")
    print("=" * 80)
    
    pivot_time = df.pivot(index='N', columns='processes', values='time_seconds')
    print("\nExecution time (seconds):")
    print("-" * 60)
    print(pivot_time.round(4))
    
    if 1 in pivot_time.columns:
        base = pivot_time[1]
        print("\nSpeedup:")
        print("-" * 60)
        for col in pivot_time.columns:
            if col != 1:
                speedup = base / pivot_time[col]
                print(f"  {int(col)} processes: {speedup.round(3)}")
        
        print("\nEfficiency:")
        print("-" * 60)
        for col in pivot_time.columns:
            if col != 1:
                efficiency = (base / pivot_time[col]) / col
                print(f"  {int(col)} processes: {efficiency.round(3)}")
    print("=" * 80)

def plot_time(df):
    print("\nPlotting time graph...")
    plt.figure()
    
    procs_list = sorted(df['processes'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(procs_list)))
    
    for procs, color in zip(procs_list, colors):
        data = df[df['processes'] == procs].sort_values('N')
        plt.plot(data['N'], data['time_seconds'], 
                 marker='o', color=color, linewidth=2, markersize=8,
                 label=f'{procs} process(es)')
    
    plt.xlabel('Matrix size (N)')
    plt.ylabel('Execution time (seconds)')
    plt.title('MPI: Execution time vs Matrix size')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'time_plot.png', dpi=150)
    plt.close()
    print(f"  Saved: {PLOTS_DIR / 'time_plot.png'}")

def plot_speedup(df):
    print("Plotting speedup graph...")
    
    if 1 not in df['processes'].values:
        print("  No data for 1 process")
        return
    
    plt.figure()
    base_times = df[df['processes'] == 1].set_index('N')['time_seconds']
    sizes = sorted(df['N'].unique())
    procs_list = sorted([p for p in df['processes'].unique() if p != 1])
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(sizes)))
    
    for size, color in zip(sizes, colors):
        speedups = []
        for procs in procs_list:
            tp_data = df[(df['N'] == size) & (df['processes'] == procs)]['time_seconds']
            if len(tp_data) > 0 and size in base_times.index:
                speedups.append(base_times[size] / tp_data.values[0])
            else:
                speedups.append(1)
        
        plt.plot(procs_list, speedups, marker='o', color=color, 
                 linewidth=2, markersize=8, label=f'N={size}')
    
    if procs_list:
        max_procs = max(procs_list)
        ideal = np.linspace(1, max_procs, 100)
        plt.plot(ideal, ideal, 'k--', linewidth=2, label='Ideal', alpha=0.7)
        plt.xlim(1, max_procs)
        plt.ylim(1, max_procs)
    
    plt.xlabel('Number of MPI processes')
    plt.ylabel('Speedup')
    plt.title('MPI: Speedup')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'speedup_plot.png', dpi=150)
    plt.close()
    print(f"  Saved: {PLOTS_DIR / 'speedup_plot.png'}")

def plot_efficiency(df):
    print("Plotting efficiency graph...")
    
    if 1 not in df['processes'].values:
        print("  No data for 1 process")
        return
    
    plt.figure()
    base_times = df[df['processes'] == 1].set_index('N')['time_seconds']
    sizes = sorted(df['N'].unique())
    procs_list = sorted([p for p in df['processes'].unique() if p != 1])
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(sizes)))
    
    for size, color in zip(sizes, colors):
        efficiencies = []
        for procs in procs_list:
            tp_data = df[(df['N'] == size) & (df['processes'] == procs)]['time_seconds']
            if len(tp_data) > 0 and size in base_times.index:
                efficiency = (base_times[size] / tp_data.values[0]) / procs
                efficiencies.append(efficiency)
            else:
                efficiencies.append(1)
        
        plt.plot(procs_list, efficiencies, marker='o', color=color,
                 linewidth=2, markersize=8, label=f'N={size}')
    
    plt.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Ideal')
    plt.xlabel('Number of MPI processes')
    plt.ylabel('Efficiency')
    plt.title('MPI: Efficiency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.2)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'efficiency_plot.png', dpi=150)
    plt.close()
    print(f"  Saved: {PLOTS_DIR / 'efficiency_plot.png'}")

def main():
    print("=" * 60)
    print("MPI Results Analysis - Lab3")
    print("=" * 60)
    
    ensure_plots_dir()
    df = load_and_aggregate()
    print_summary_table(df)
    
    print("\nGenerating plots...")
    plot_time(df)
    plot_speedup(df)
    plot_efficiency(df)
    
    print("\n" + "=" * 60)
    print(f"Done! Plots saved to: {PLOTS_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()