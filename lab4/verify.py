import numpy as np
import sys

if len(sys.argv) != 4:
    print("Usage: python verify.py matrixA.txt matrixB.txt result.txt")
    sys.exit(1)

A = np.loadtxt(sys.argv[1], skiprows=1)
B = np.loadtxt(sys.argv[2], skiprows=1)
C = np.loadtxt(sys.argv[3], skiprows=1)

expected = np.dot(A, B)

if np.allclose(C, expected, atol=1e-5):
    print("✓ Verification passed!")
else:
    print("✗ Verification failed!")
    diff = np.abs(C - expected)
    print(f"Max difference: {np.max(diff)}")