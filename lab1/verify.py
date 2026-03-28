import numpy as np
import sys

if len(sys.argv) != 4:
    print("Usage: python verify.py matrixA.txt matrixB.txt result.txt")
    sys.exit(1)

fileA = sys.argv[1]
fileB = sys.argv[2]
fileResult = sys.argv[3]

# Чтение матриц (пропускаем первую строку)
A = np.loadtxt(fileA, skiprows=1)
B = np.loadtxt(fileB, skiprows=1)
C = np.loadtxt(fileResult, skiprows=1)

# Ожидаемый результат
expected = np.dot(A, B)

# Сравнение
if np.allclose(C, expected, atol=1e-6):
    print("Verification passed!")
else:
    print("Verification failed!")
    print("Differences:")
    print(C - expected)