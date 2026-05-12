# -*- coding: utf-8 -*-
import sys

def read_matrix(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    N = int(lines[0].strip())
    matrix = []
    for i in range(1, N+1):
        row = list(map(float, lines[i].strip().split()))
        matrix.append(row)
    return N, matrix

def multiply_matrices(A, B, N):
    result = [[0.0] * N for _ in range(N)]
    for i in range(N):
        for k in range(N):
            aik = A[i][k]
            for j in range(N):
                result[i][j] += aik * B[k][j]
    return result

def matrices_equal(C, expected, eps=1e-6):
    for i in range(len(C)):
        for j in range(len(C)):
            if abs(C[i][j] - expected[i][j]) > eps:
                print("Difference at [{},{}]: {} vs {}".format(i, j, C[i][j], expected[i][j]))
                return False
    return True

if len(sys.argv) != 4:
    print("Usage: python verify.py matrixA.txt matrixB.txt result.txt")
    sys.exit(1)

print("Reading matrices...")
_, A = read_matrix(sys.argv[1])
_, B = read_matrix(sys.argv[2])
_, C = read_matrix(sys.argv[3])
N = len(A)

print("Computing expected result...")
expected = multiply_matrices(A, B, N)

print("Comparing results...")
if matrices_equal(C, expected):
    print("Verification passed!")
else:
    print("Verification failed!")