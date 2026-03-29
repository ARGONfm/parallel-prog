#!/bin/bash
#SBATCH --job-name=matrix_mpi
#SBATCH --time=00:30:00
#SBATCH --ntasks=8
#SBATCH --nodes=1
#SBATCH --partition=batch
#SBATCH --output=result_%j.out

# Загружаем модуль MPI (уточнить на кластере!)
module load intel/mpi4

# Запуск
mpirun ./matrix_mpi matrixA.txt matrixB.txt result.txt