import numpy as np
import sys

if len(sys.argv) != 2:
    print("Usage: python generate_matrix.py N")
    sys.exit(1)

N = int(sys.argv[1])

# Генерация случайных матриц типа float32
A = np.random.rand(N, N).astype(np.float32)
B = np.random.rand(N, N).astype(np.float32)

with open('matrixA.txt', 'w') as f:
    f.write(f"{N}\n")
    np.savetxt(f, A, fmt='%.6f')

with open('matrixB.txt', 'w') as f:
    f.write(f"{N}\n")
    np.savetxt(f, B, fmt='%.6f')

print(f"Matrices generated for N={N}")