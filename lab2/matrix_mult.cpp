#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <omp.h>
#include <string>
#include <windows.h>

void set_process_affinity(int cores) {
#ifdef _WIN32
    HANDLE process = GetCurrentProcess();
    DWORD_PTR processAffinityMask = 0;

    for (int i = 0; i < cores && i < 64; i++) {
        processAffinityMask |= (1ULL << i);
    }

    DWORD_PTR systemAffinityMask;
    if (GetProcessAffinityMask(process, &processAffinityMask, &systemAffinityMask)) {
        processAffinityMask &= systemAffinityMask;
        SetProcessAffinityMask(process, processAffinityMask);
        std::cout << "Process affinity set to " << cores << " cores" << std::endl;
    }
#else
    (void)cores;
#endif
}

void multiply_matrices(const std::vector<std::vector<double>>& A,
    const std::vector<std::vector<double>>& B,
    std::vector<std::vector<double>>& C,
    int N) {

#pragma omp parallel for
    for (int i = 0; i < N; ++i) {
        for (int k = 0; k < N; ++k) {
            double aik = A[i][k];
            for (int j = 0; j < N; ++j) {
                C[i][j] += aik * B[k][j];
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <matrixA> <matrixB> <result> <threads> [cores]" << std::endl;
        return 1;
    }

    std::string fileA = argv[1];
    std::string fileB = argv[2];
    std::string fileResult = argv[3];
    int num_threads = std::stoi(argv[4]);

    // Установка количества потоков OpenMP
    omp_set_num_threads(num_threads);

    // Установка affinity процесса (если указано)
    if (argc > 5) {
        int num_cores = std::stoi(argv[5]);
        set_process_affinity(num_cores);
    }

    std::cout << "OpenMP threads: " << num_threads << std::endl;

    std::ifstream inA(fileA);
    if (!inA) {
        std::cerr << "Cannot open " << fileA << std::endl;
        return 1;
    }
    int N;
    inA >> N;
    std::vector<std::vector<double>> A(N, std::vector<double>(N));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            inA >> A[i][j];
        }
    }
    inA.close();

    std::ifstream inB(fileB);
    if (!inB) {
        std::cerr << "Cannot open " << fileB << std::endl;
        return 1;
    }
    int M;
    inB >> M;
    if (M != N) {
        std::cerr << "Matrices must be square and of the same size" << std::endl;
        return 1;
    }
    std::vector<std::vector<double>> B(N, std::vector<double>(N));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            inB >> B[i][j];
        }
    }
    inB.close();

    std::vector<std::vector<double>> C(N, std::vector<double>(N, 0.0));

    // Измерение времени
    auto start = std::chrono::high_resolution_clock::now();

    multiply_matrices(A, B, C, N);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::ofstream out(fileResult);
    if (!out) {
        std::cerr << "Cannot open " << fileResult << std::endl;
        return 1;
    }
    out << N << std::endl;
    out << std::fixed << std::setprecision(6);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            out << C[i][j] << " ";
        }
        out << std::endl;
    }
    out.close();

    long long volume = static_cast<long long>(N) * N * N;
    std::cout << "Execution time: " << duration.count() << " seconds" << std::endl;
    std::cout << "Task volume: " << volume << " operations" << std::endl;
    std::cout << "Matrix size: " << N << "x" << N << std::endl;
    std::cout << "Threads: " << num_threads << std::endl;

    return 0;
}