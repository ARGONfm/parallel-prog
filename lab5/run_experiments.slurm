#!/bin/bash
#SBATCH --job-name=matrix_exp
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --partition=batch

module load intel/mpi4

SIZES=(200 400 800 1200 1600 2000)
PROCS=(1 2 4 8)

echo "N,processes,run,time_seconds" > experiment_results.csv

for n in "${SIZES[@]}"; do
    echo "Generating N=$n"
    python generate_matrix.py $n
    
    for p in "${PROCS[@]}"; do
        for run in 1 2 3; do
            echo "  Running: processes=$p, run=$run"
            OUTPUT=$(mpirun -np $p ./matrix_mpi matrixA.txt matrixB.txt result.txt)
            TIME=$(echo "$OUTPUT" | grep "Execution time:" | awk '{print $4}')
            echo "$n,$p,$run,$TIME" >> experiment_results.csv
            sleep 1
        done
    done
done

echo "Done! Results in experiment_results.csv"
