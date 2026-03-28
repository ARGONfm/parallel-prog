import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Настройка графиков
plt.style.use('ggplot')
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (12, 8)

RESULTS_FILE = "experiment_results.csv"
PLOTS_DIR = Path("plots")

def ensure_plots_dir():
    PLOTS_DIR.mkdir(exist_ok=True)

def load_and_aggregate():
    print("Загрузка результатов...")
    if not Path(RESULTS_FILE).exists():
        print(f"Ошибка: файл {RESULTS_FILE} не найден!")
        sys.exit(1)
    
    df = pd.read_csv(RESULTS_FILE)
    df_mean = df.groupby(['N', 'threads'])['time_seconds'].mean().reset_index()
    return df_mean

def print_summary_table(df):
    print("\n" + "=" * 80)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 80)
    
    pivot_time = df.pivot(index='N', columns='threads', values='time_seconds')
    print("\nВремя выполнения (секунды):")
    print("-" * 60)
    print(pivot_time.round(4))
    
    if 1 in pivot_time.columns:
        base = pivot_time[1]
        print("\nУскорение:")
        print("-" * 60)
        speedup_data = {}
        for col in pivot_time.columns:
            if col != 1:
                speedup = base / pivot_time[col]
                speedup_data[col] = speedup
                print(f"  {int(col)} потоков:")
                print(speedup.round(3))
        
        print("\nЭффективность:")
        print("-" * 60)
        for col in pivot_time.columns:
            if col != 1:
                efficiency = (base / pivot_time[col]) / col
                print(f"  {int(col)} потоков:")
                print(efficiency.round(3))
    
    print("=" * 80)

def plot_time(df):
    """График времени выполнения от размера матрицы"""
    print("\nПостроение графика времени...")
    plt.figure()
    
    threads_list = sorted(df['threads'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(threads_list)))
    
    for threads, color in zip(threads_list, colors):
        data = df[df['threads'] == threads].sort_values('N')
        plt.plot(data['N'], data['time_seconds'], 
                 marker='o', color=color, linewidth=2, markersize=8,
                 label=f'{threads} поток(ов)')
    
    plt.xlabel('Размер матрицы (N)')
    plt.ylabel('Время выполнения (секунды)')
    plt.title('Зависимость времени выполнения от размера матрицы')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'time_plot.png', dpi=150)
    plt.close()
    print(f"  Сохранён: {PLOTS_DIR / 'time_plot.png'}")

def plot_speedup(df):
    """График ускорения от количества потоков"""
    print("Построение графика ускорения...")
    
    if 1 not in df['threads'].values:
        print("  Нет данных для 1 потока")
        return
    
    plt.figure()
    base_times = df[df['threads'] == 1].set_index('N')['time_seconds']
    sizes = sorted(df['N'].unique())
    threads_list = sorted([t for t in df['threads'].unique() if t != 1])
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(sizes)))
    
    for size, color in zip(sizes, colors):
        speedups = []
        for threads in threads_list:
            tp_data = df[(df['N'] == size) & (df['threads'] == threads)]['time_seconds']
            if len(tp_data) > 0 and size in base_times.index:
                speedups.append(base_times[size] / tp_data.values[0])
            else:
                speedups.append(1)
        
        plt.plot(threads_list, speedups, marker='o', color=color, 
                 linewidth=2, markersize=8, label=f'N={size}')
    
    # Идеальное ускорение
    if threads_list:
        max_threads = max(threads_list)
        ideal = np.linspace(1, max_threads, 100)
        plt.plot(ideal, ideal, 'k--', linewidth=2, label='Идеальное', alpha=0.7)
        plt.xlim(1, max_threads)
        plt.ylim(1, max_threads)
    
    plt.xlabel('Количество потоков')
    plt.ylabel('Ускорение')
    plt.title('Ускорение при параллельном выполнении')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'speedup_plot.png', dpi=150)
    plt.close()
    print(f"  Сохранён: {PLOTS_DIR / 'speedup_plot.png'}")

def plot_efficiency(df):
    """График эффективности распараллеливания"""
    print("Построение графика эффективности...")
    
    if 1 not in df['threads'].values:
        print("  Нет данных для 1 потока")
        return
    
    plt.figure()
    base_times = df[df['threads'] == 1].set_index('N')['time_seconds']
    sizes = sorted(df['N'].unique())
    threads_list = sorted([t for t in df['threads'].unique() if t != 1])
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(sizes)))
    
    for size, color in zip(sizes, colors):
        efficiencies = []
        for threads in threads_list:
            tp_data = df[(df['N'] == size) & (df['threads'] == threads)]['time_seconds']
            if len(tp_data) > 0 and size in base_times.index:
                efficiency = (base_times[size] / tp_data.values[0]) / threads
                efficiencies.append(efficiency)
            else:
                efficiencies.append(1)
        
        plt.plot(threads_list, efficiencies, marker='o', color=color,
                 linewidth=2, markersize=8, label=f'N={size}')
    
    plt.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Идеальная')
    plt.xlabel('Количество потоков')
    plt.ylabel('Эффективность')
    plt.title('Эффективность распараллеливания')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.2)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'efficiency_plot.png', dpi=150)
    plt.close()
    print(f"  Сохранён: {PLOTS_DIR / 'efficiency_plot.png'}")

def plot_scalability_comparison(df):
    """Сравнение ускорения и эффективности"""
    print("Построение сравнительного графика...")
    
    if 1 not in df['threads'].values:
        print("  Нет данных для 1 потока")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    base_times = df[df['threads'] == 1].set_index('N')['time_seconds']
    sizes = sorted(df['N'].unique())
    threads_list = sorted([t for t in df['threads'].unique() if t != 1])
    
    if not threads_list:
        return
    
    # График ускорения
    ax1 = axes[0]
    for size in sizes:
        speedups = []
        for threads in threads_list:
            tp_data = df[(df['N'] == size) & (df['threads'] == threads)]['time_seconds']
            if len(tp_data) > 0 and size in base_times.index:
                speedups.append(base_times[size] / tp_data.values[0])
            else:
                speedups.append(1)
        
        ax1.plot(threads_list, speedups, marker='o', linewidth=2, label=f'N={size}')
    
    ax1.plot(threads_list, threads_list, 'k--', linewidth=2, label='Идеальное')
    ax1.set_xlabel('Количество потоков')
    ax1.set_ylabel('Ускорение')
    ax1.set_title('Ускорение')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # График эффективности
    ax2 = axes[1]
    for size in sizes:
        efficiencies = []
        for threads in threads_list:
            tp_data = df[(df['N'] == size) & (df['threads'] == threads)]['time_seconds']
            if len(tp_data) > 0 and size in base_times.index:
                efficiency = (base_times[size] / tp_data.values[0]) / threads
                efficiencies.append(efficiency)
            else:
                efficiencies.append(1)
        
        ax2.plot(threads_list, efficiencies, marker='o', linewidth=2, label=f'N={size}')
    
    ax2.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Идеальная')
    ax2.set_xlabel('Количество потоков')
    ax2.set_ylabel('Эффективность')
    ax2.set_title('Эффективность')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.2)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'scalability_comparison.png', dpi=150)
    plt.close()
    print(f"  Сохранён: {PLOTS_DIR / 'scalability_comparison.png'}")

def main():
    print("=" * 60)
    print("Анализ результатов экспериментов")
    print("Лабораторная работа №2: Исследование масштабируемости OpenMP")
    print("=" * 60)
    
    ensure_plots_dir()
    df = load_and_aggregate()
    print_summary_table(df)
    
    print("\nПостроение графиков...")
    plot_time(df)
    plot_speedup(df)
    plot_efficiency(df)
    plot_scalability_comparison(df)
    
    print("\n" + "=" * 60)
    print(f"Готово! Все графики сохранены в папку: {PLOTS_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()