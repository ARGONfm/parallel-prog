import numpy as np
import sys

if len(sys.argv) != 2:
    print("Usage: python generate_matrices.py N")
    sys.exit(1)

N = int(sys.argv[1])

# Генерация случайных матриц (0-1)
A = np.random.rand(N, N)
B = np.random.rand(N, N)

# Запись A
with open('matrixA.txt', 'w') as f:
    f.write(f"{N}\n")
    np.savetxt(f, A, fmt='%.6f')

# Запись B
with open('matrixB.txt', 'w') as f:
    f.write(f"{N}\n")
    np.savetxt(f, B, fmt='%.6f')

print(f"Matrices generated for N={N}")