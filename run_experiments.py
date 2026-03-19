import subprocess
import sys
import time
import os

# НАСТРОЙКИ ЭКСПЕРИМЕНТА
MATRIX_SIZES = [200, 400, 800, 1200, 1600, 2000]
THREAD_COUNTS = [1, 2, 4, 8]
NUM_RUNS = 3

# Пути к файлам
MATRIX_A = "matrixA.txt"
MATRIX_B = "matrixB.txt"
RESULT_FILE = "result.txt"
GENERATOR_SCRIPT = "generate_matrix.py"
PROGRAM_PATH = "build-release/Release/matrix_mult.exe"
VERIFY_SCRIPT = "verify.py"

# Файл для логирования результатов
LOG_FILE = "experiment_results.csv"

def run_experiment(n, threads):
    """Сгенерировать матрицы, запустить программу, вернуть время выполнения."""
    print(f"  Выполнение: N={n}, threads={threads}...", end="", flush=True)

    # 1. Генерация матриц
    gen_result = subprocess.run([sys.executable, GENERATOR_SCRIPT, str(n)], capture_output=True, text=True)
    if gen_result.returncode != 0:
        print(f" Ошибка генерации!")
        return None

    # 2. Запуск программы
    try:
        proc = subprocess.run([PROGRAM_PATH, MATRIX_A, MATRIX_B, RESULT_FILE, str(threads)],
                               capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print(f" Таймаут!")
        return None
    except FileNotFoundError:
        print(f"\nОШИБКА: {PROGRAM_PATH} не найден. Сначала соберите программу.")
        sys.exit(1)

    if proc.returncode != 0:
        print(f" Ошибка программы!")
        return None

    # 3. Проверка результата (опционально)
    verify_result = subprocess.run([sys.executable, VERIFY_SCRIPT, MATRIX_A, MATRIX_B, RESULT_FILE])
    if verify_result.returncode != 0:
        print(f" Проверка не пройдена!")

    # 4. Извлечение времени выполнения из вывода
    for line in proc.stdout.split('\n'):
        if "Execution time:" in line:
            time_str = line.split(':')[1].strip().split()[0]
            print(f" время = {time_str} с")
            return float(time_str)

    print(f" Не удалось найти время выполнения в выводе")
    return None

print("Запуск экспериментов...")
print("Результаты будут сохранены в", LOG_FILE)

with open(LOG_FILE, 'w') as f:
    f.write("N,threads,run,time_seconds\n")

total_runs = len(MATRIX_SIZES) * len(THREAD_COUNTS) * NUM_RUNS
current_run = 0

for n in MATRIX_SIZES:
    for threads in THREAD_COUNTS:
        for run_num in range(1, NUM_RUNS + 1):
            current_run += 1
            print(f"[{current_run}/{total_runs}]")
            exec_time = run_experiment(n, threads)

            if exec_time is not None:
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{n},{threads},{run_num},{exec_time:.6f}\n")
            else:
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{n},{threads},{run_num},ERROR\n")
            time.sleep(1)

print(f"\nЭксперименты завершены! Все результаты в {LOG_FILE}")