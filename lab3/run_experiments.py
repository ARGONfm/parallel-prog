import subprocess
import sys
import time
import csv
import os

MATRIX_SIZES = [200, 400, 800, 1200, 1600, 2000]
PROCESS_COUNTS = [1, 2, 4, 8]
NUM_RUNS = 3

PROGRAM_PATH = "matrix_mpi.exe"
GENERATOR_SCRIPT = "generate_matrix.py"
RESULTS_FILE = "experiment_results.csv"

def run_experiment(n, procs):
    print(f"  N={n}, procs={procs}: generating...", end=" ", flush=True)
    subprocess.run([sys.executable, GENERATOR_SCRIPT, str(n)], capture_output=True, check=True)
    print("OK", end=" ", flush=True)
    
    print("running...", end=" ", flush=True)
    cmd = ["mpiexec", "-n", str(procs), PROGRAM_PATH, "matrixA.txt", "matrixB.txt", "result.txt"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    for line in proc.stdout.split('\n'):
        if "Execution time:" in line:
            time_str = line.split(':')[1].strip().split()[0]
            print(f"time={time_str} sec")
            return float(time_str)
    print("ERROR")
    return None

def main():
    print("=" * 50)
    print("MPI Experiments")
    print("=" * 50)
    
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['N', 'processes', 'run', 'time_seconds'])
        
        for n in MATRIX_SIZES:
            for procs in PROCESS_COUNTS:
                for run_num in range(1, NUM_RUNS + 1):
                    print(f"\n[{n}x{n}, procs={procs}, run={run_num}]")
                    exec_time = run_experiment(n, procs)
                    if exec_time:
                        writer.writerow([n, procs, run_num, exec_time])
                    time.sleep(0.5)
    
    print(f"\nResults saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()