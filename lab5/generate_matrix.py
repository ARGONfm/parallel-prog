# -*- coding: utf-8 -*-
import sys
import random

if len(sys.argv) != 2:
    print("Usage: python generate_matrix.py N")
    sys.exit(1)

N = int(sys.argv[1])

def generate_matrix(filename, N):
    with open(filename, 'w') as f:
        f.write("{}\n".format(N))
        for i in range(N):
            row = []
            for j in range(N):
                # Генерация случайного числа от 0 до 1
                val = random.uniform(0, 1)
                row.append("{:.6f}".format(val))
            f.write(" ".join(row) + "\n")
    print("  Saved {}".format(filename))

print("Generating matrices for N={}".format(N))
generate_matrix('matrixA.txt', N)
generate_matrix('matrixB.txt', N)
print("Done!")