#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.style.use('ggplot')
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (12, 8)

RESULTS_FILE = "experiment_results.csv"
PLOTS_DIR = Path("plots")

def ensure_plots_dir():
    PLOTS_DIR.mkdir(exist_ok=True)

def load_and_aggregate():
    df = pd.read_csv(RESULTS_FILE)
    df_mean = df.groupby(['N', 'block_size', 'kernel_type'])['time_seconds'].mean().reset_index()
    return df_mean

def plot_comparison(df):
    print("Plotting time comparison...")
    plt.figure()
    
    kernel_names = {0: 'Basic', 1: 'Shared Memory'}
    markers = ['o', 's', '^', 'D']
    colors = plt.cm.viridis(np.linspace(0, 1, 4))
    
    for i, (block_size, color) in enumerate(zip([16, 32], colors[:2])):
        for kernel_type in [0, 1]:
            data = df[(df['block_size'] == block_size) & (df['kernel_type'] == kernel_type)].sort_values('N')
            label = f"{kernel_names[kernel_type]}, block {block_size}x{block_size}"
            marker = 'o' if kernel_type == 0 else 's'
            plt.plot(data['N'], data['time_seconds'], 
                     marker=marker, color=color, linewidth=2, markersize=8,
                     label=label)
    
    plt.xlabel('Matrix size (N)')
    plt.ylabel('Execution time (seconds)')
    plt.title('CUDA: Execution time vs Matrix size')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'time_comparison.png', dpi=150)
    plt.close()
    print(f"  Saved: {PLOTS_DIR / 'time_comparison.png'}")

def plot_speedup_vs_basic(df):
    print("Plotting speedup vs basic kernel...")
    plt.figure()
    
    base = df[(df['kernel_type'] == 0) & (df['block_size'] == 16)].set_index('N')['time_seconds']
    sizes = sorted(df['N'].unique())
    
    for block_size in [16, 32]:
        for kernel_type in [1]:
            data = df[(df['kernel_type'] == kernel_type) & (df['block_size'] == block_size)].set_index('N')['time_seconds']
            speedups = [base[n] / data[n] for n in sizes if n in data.index]
            label = f"Shared memory, block {block_size}x{block_size}"
            marker = '^' if block_size == 16 else 'D'
            plt.plot(sizes[:len(speedups)], speedups, marker=marker, linewidth=2, markersize=8, label=label)
    
    plt.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='Basic kernel baseline')
    plt.xlabel('Matrix size (N)')
    plt.ylabel('Speedup vs Basic 16x16')
    plt.title('CUDA: Speedup comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'speedup_plot.png', dpi=150)
    plt.close()
    print(f"  Saved: {PLOTS_DIR / 'speedup_plot.png'}")

def print_summary_table(df):
    print("\n" + "=" * 80)
    print("SUMMARY TABLE (CUDA)")
    print("=" * 80)
    
    pivot = df.pivot_table(index='N', columns=['block_size', 'kernel_type'], values='time_seconds')
    print("\nExecution time (seconds):")
    print("-" * 60)
    print(pivot.round(6))
    print("=" * 80)

def main():
    print("=" * 60)
    print("CUDA Results Analysis - Lab4")
    print("=" * 60)
    
    ensure_plots_dir()
    df = load_and_aggregate()
    print_summary_table(df)
    
    print("\nGenerating plots...")
    plot_comparison(df)
    plot_speedup_vs_basic(df)
    
    print(f"\nDone! Plots saved to: {PLOTS_DIR}")

if __name__ == "__main__":
    main()