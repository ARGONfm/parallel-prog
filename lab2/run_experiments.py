import subprocess
import sys
import time
import csv
import os

MATRIX_SIZES = [200, 400, 800, 1200, 1600, 2000]
THREAD_COUNTS = [1, 2, 4, 8]
NUM_RUNS = 3
PROGRAM_PATH = "matrix_mult.exe"
GENERATOR_SCRIPT = "generate_matrix.py"
VERIFY_SCRIPT = "verify.py"
RESULTS_FILE = "experiment_results.csv"

def run_experiment(n, threads):
    print(f"    Генерация матриц {n}x{n}...", end="", flush=True)
    gen_result = subprocess.run(
        [sys.executable, GENERATOR_SCRIPT, str(n)],
        capture_output=True, text=True
    )
    if gen_result.returncode != 0:
        print(" ОШИБКА")
        return None
    print(" OK")
    
    print(f"    Запуск с {threads} потоками...", end="", flush=True)
    cmd = [PROGRAM_PATH, "matrixA.txt", "matrixB.txt", "result.txt", str(threads)]
    
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(" ТАЙМАУТ")
        return None
    except FileNotFoundError:
        print(f"\nОШИБКА: {PROGRAM_PATH} не найден!")
        return None
    
    if proc.returncode != 0:
        print(" ОШИБКА")
        return None
    print(" OK")
    
    for line in proc.stdout.split('\n'):
        if "Execution time:" in line:
            time_str = line.split(':')[1].strip().split()[0]
            return float(time_str)
    
    return None

def main():
    print("=" * 60)
    print("Запуск экспериментов")
    print("=" * 60)
    
    if not os.path.exists(PROGRAM_PATH):
        print(f"ОШИБКА: {PROGRAM_PATH} не найден!")
        return
    
    total = len(MATRIX_SIZES) * len(THREAD_COUNTS) * NUM_RUNS
    print(f"Всего экспериментов: {total}")
    
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['N', 'threads', 'run', 'time_seconds'])
        
        current = 0
        for n in MATRIX_SIZES:
            for threads in THREAD_COUNTS:
                print(f"\n[{n}x{n}, threads={threads}]")
                
                for run_num in range(1, NUM_RUNS + 1):
                    current += 1
                    print(f"  Запуск {run_num}/{NUM_RUNS} ({current}/{total})")
                    
                    exec_time = run_experiment(n, threads)
                    
                    if exec_time is not None:
                        writer.writerow([n, threads, run_num, exec_time])
                        print(f"    Время: {exec_time:.4f} сек")
                    else:
                        writer.writerow([n, threads, run_num, 'ERROR'])
                        print(f"    ОШИБКА")
                    
                    time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"Готово! Результаты в {RESULTS_FILE}")

if __name__ == "__main__":
    main()
