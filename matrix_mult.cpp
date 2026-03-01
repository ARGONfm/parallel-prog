#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <omp.h>
#include <string>

int main(int argc, char* argv[]) {
    if (argc != 5) {
        std::cerr << "Usage: " << argv[0] << " matrixA.txt matrixB.txt result.txt num_threads" << std::endl;
        return 1;
    }

    std::string fileA = argv[1];
    std::string fileB = argv[2];
    std::string fileResult = argv[3];
    int num_threads = std::stoi(argv[4]);

    // Установка числа потоков
    omp_set_num_threads(num_threads);

    // Чтение матрицы A
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

    // Чтение матрицы B
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

    // Подготовка результирующей матрицы
    std::vector<std::vector<double>> C(N, std::vector<double>(N, 0.0));

    // Измерение времени
    auto start = std::chrono::high_resolution_clock::now();

    // Параллельное перемножение матриц
    #pragma omp parallel for 
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            for (int k = 0; k < N; ++k) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    // Запись результата в файл
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

    // Вывод времени и объема
    long long volume = static_cast<long long>(N) * N * N;
    std::cout << "Execution time: " << duration.count() << " seconds" << std::endl;
    std::cout << "Task volume: " << volume << " operations" << std::endl;
    std::cout << "Number of threads: " << num_threads << std::endl;

    return 0;
}