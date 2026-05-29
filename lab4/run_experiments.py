#!/usr/bin/env python3
import subprocess
import sys
import time
import csv
import os

MATRIX_SIZES = [200, 400, 800, 1200, 1600, 2000]
BLOCK_SIZES = [16, 32]
KERNEL_TYPES = [0, 1]  # 0 - basic, 1 - shared memory
NUM_RUNS = 3

PROGRAM_PATH = "matrix_cuda.exe"
GENERATOR_SCRIPT = "generate_matrix.py"
RESULTS_FILE = "experiment_results.csv"

def run_experiment(n, block_size, kernel_type):
    kernel_name = "shared" if kernel_type else "basic"
    print(f"  N={n}, block={block_size}, kernel={kernel_name}...", end=" ", flush=True)
    
    subprocess.run([sys.executable, GENERATOR_SCRIPT, str(n)], capture_output=True)
    
    cmd = [PROGRAM_PATH, "matrixA.txt", "matrixB.txt", "result.txt", str(block_size), str(kernel_type)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    
    for line in proc.stdout.split('\n'):
        if "Execution time:" in line:
            time_str = line.split(':')[1].strip().split()[0]
            print(f"time={time_str} sec")
            return float(time_str)
    
    print("ERROR")
    return None

def main():
    print("=" * 60)
    print("CUDA Matrix Multiplication Experiments - Lab4")
    print("=" * 60)
    
    total = len(MATRIX_SIZES) * len(BLOCK_SIZES) * len(KERNEL_TYPES) * NUM_RUNS
    print(f"Total experiments: {total}")
    
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['N', 'block_size', 'kernel_type', 'run', 'time_seconds'])
        
        current = 0
        for n in MATRIX_SIZES:
            for block_size in BLOCK_SIZES:
                for kernel_type in KERNEL_TYPES:
                    for run_num in range(1, NUM_RUNS + 1):
                        current += 1
                        print(f"\n[{n}x{n}, block={block_size}, kernel={'shared' if kernel_type else 'basic'}, run={run_num}] ({current}/{total})")
                        exec_time = run_experiment(n, block_size, kernel_type)
                        if exec_time:
                            writer.writerow([n, block_size, kernel_type, run_num, exec_time])
                        time.sleep(0.5)
    
    print(f"\nResults saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()