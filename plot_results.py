import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Проверка наличия файла
print("Проверка наличия файла...")
if not os.path.exists('experiment_results.csv'):
    print("ОШИБКА: Файл experiment_results.csv не найден!")
    print("Текущая директория:", os.getcwd())
    print("Файлы в директории:")
    for file in os.listdir('.'):
        print(f"  - {file}")
    sys.exit(1)

print("Файл найден. Пытаемся прочитать...")

# Чтение CSV с разделителем ;
try:
    df = pd.read_csv('experiment_results.csv', sep=';', 
                     encoding='utf-8', 
                     skipinitialspace=True)
    print("Файл прочитан через pandas")
except Exception as e:
    print(f"Ошибка при чтении через pandas: {e}")
    print("Пробуем прочитать вручную...")
    
    # Ручное чтение файла
    data = []
    with open('experiment_results.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        header = lines[0].strip().split(',')
        header = [h.strip() for h in header]
        print(f"Заголовок: {header}")
        
        for line in lines[1:]:
            if line.strip():
                values = line.strip().split(',')
                values = [v.strip() for v in values]
                data.append(values)
    
    df = pd.DataFrame(data, columns=header)
    print("DataFrame создан вручную")

print("\nИнформация о данных:")
print(f"Колонки: {df.columns.tolist()}")
print(f"Размер: {df.shape}")
print(f"Типы данных:\n{df.dtypes}")
print(f"\nПервые 5 строк:\n{df.head()}")

# Преобразование в числовые типы
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
        print(f"Колонка {col} преобразована в числовой тип")
    except:
        print(f"Колонка {col} оставлена как есть (не числовая)")

# Создание папки для графиков
if not os.path.exists('plots'):
    os.makedirs('plots')
    print("\nСоздана папка 'plots'")

# Проверка наличия необходимых колонок
required_columns = ['N', 'threads', 'time_seconds']
for col in required_columns:
    if col not in df.columns:
        print(f"ОШИБКА: Колонка '{col}' не найдена!")
        print(f"Доступные колонки: {df.columns.tolist()}")
        sys.exit(1)

print("\nВсе необходимые колонки найдены. Строим графики...")

# Усреднение по запускам
df_mean = df.groupby(['N', 'threads'])['time_seconds'].mean().reset_index()
print(f"Усредненные данные:\n{df_mean}")

# Настройки графиков
colors = ['blue', 'green', 'red', 'purple']
markers = ['o', 's', '^', 'D']

# График времени выполнения
plt.figure(figsize=(14, 8))
threads_list = sorted(df_mean['threads'].unique())

for i, threads in enumerate(threads_list):
    data = df_mean[df_mean['threads'] == threads].sort_values('N')
    plt.plot(data['N'], data['time_seconds'], 
             marker=markers[i % len(markers)], 
             color=colors[i % len(colors)], 
             linewidth=2, 
             label=f'{threads} поток(ов)', 
             markersize=8)

plt.xlabel('Размер матрицы (N)', fontsize=12)
plt.ylabel('Время выполнения (с)', fontsize=12)
plt.title('Зависимость времени выполнения от размера матрицы', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, linestyle='--')
plt.yscale('log')
plt.xscale('log')

plt.tight_layout()
plt.savefig('plots/time_plot.png', dpi=150, bbox_inches='tight')
print("✓ График времени сохранён: plots/time_plot.png")
plt.close()

# График ускорения
if 1 in threads_list:
    plt.figure(figsize=(14, 8))
    base_times = df_mean[df_mean['threads'] == 1].set_index('N')['time_seconds']
    
    for i, threads in enumerate([t for t in threads_list if t != 1]):
        speedup = []
        sizes = []
        for n in sorted(df_mean['N'].unique()):
            if n in base_times.index:
                t1 = base_times[n]
                tp_data = df_mean[(df_mean['N'] == n) & (df_mean['threads'] == threads)]['time_seconds']
                if len(tp_data) > 0:
                    tp = tp_data.values[0]
                    speedup.append(t1 / tp)
                    sizes.append(n)
        
        if speedup:
            plt.plot(sizes, speedup, 
                     marker=markers[i % len(markers)], 
                     color=colors[i % len(colors)], 
                     linewidth=2, 
                     label=f'{threads} поток(ов)', 
                     markersize=8)
    
    if sizes:
        plt.plot(sizes, sizes, 'k--', alpha=0.7, linewidth=2, label='Идеальное ускорение')
    
    plt.xlabel('Размер матрицы (N)', fontsize=12)
    plt.ylabel('Ускорение', fontsize=12)
    plt.title('Ускорение при параллельном выполнении', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('plots/speedup_plot.png', dpi=150, bbox_inches='tight')
    print("✓ График ускорения сохранён: plots/speedup_plot.png")
    plt.close()
else:
    print("⚠ Данные для 1 потока не найдены, график ускорения не построен")

print(f"\nГотово! Графики сохранены в папку 'plots'")