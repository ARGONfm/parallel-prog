#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <cuda_runtime.h>

using namespace std;

// Проверка CUDA ошибок
#define CHECK_CUDA_ERROR(call) { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        cerr << "CUDA error at " << __FILE__ << ":" << __LINE__ << " - " << cudaGetErrorString(err) << endl; \
        exit(1); \
    } \
}

__global__ void matrixMulKernel(const float* A, const float* B, float* C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < N && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < N; ++k) {
            sum += A[row * N + k] * B[k * N + col];
        }
        C[row * N + col] = sum;
    }
}

void read_matrix(const string& filename, vector<float>& matrix, int& N) {
    ifstream file(filename);
    if (!file) {
        cerr << "Cannot open " << filename << endl;
        exit(1);
    }
    file >> N;
    matrix.resize(N * N);
    for (int i = 0; i < N * N; ++i) {
        file >> matrix[i];
    }
    file.close();
}

void write_matrix(const string& filename, const vector<float>& matrix, int N) {
    ofstream file(filename);
    if (!file) {
        cerr << "Cannot open " << filename << endl;
        return;
    }
    file << N << endl;
    file << fixed << setprecision(6);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            file << matrix[i * N + j] << " ";
        }
        file << endl;
    }
    file.close();
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        cerr << "Usage: " << argv[0] << " <matrixA> <matrixB> <result> <block_size>" << endl;
        return 1;
    }

    string fileA = argv[1];
    string fileB = argv[2];
    string fileResult = argv[3];
    int block_size = atoi(argv[4]);

    // Показать информацию о GPU
    int deviceCount;
    cudaGetDeviceCount(&deviceCount);
    cout << "Found " << deviceCount << " CUDA devices" << endl;

    if (deviceCount > 0) {
        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, 0);
        cout << "GPU: " << prop.name << endl;
        cout << "Compute capability: " << prop.major << "." << prop.minor << endl;
    }

    // Чтение матриц
    vector<float> A, B, C;
    int N;
    read_matrix(fileA, A, N);
    read_matrix(fileB, B, N);
    C.resize(N * N);

    cout << "Matrix size: " << N << endl;

    // Выделение памяти на GPU
    float* d_A, * d_B, * d_C;
    size_t size = N * N * sizeof(float);

    CHECK_CUDA_ERROR(cudaMalloc(&d_A, size));
    CHECK_CUDA_ERROR(cudaMalloc(&d_B, size));
    CHECK_CUDA_ERROR(cudaMalloc(&d_C, size));

    // Копирование на GPU
    CHECK_CUDA_ERROR(cudaMemcpy(d_A, A.data(), size, cudaMemcpyHostToDevice));
    CHECK_CUDA_ERROR(cudaMemcpy(d_B, B.data(), size, cudaMemcpyHostToDevice));

    // Конфигурация
    dim3 threadsPerBlock(block_size, block_size);
    dim3 numBlocks((N + block_size - 1) / block_size, (N + block_size - 1) / block_size);

    cout << "Grid size: " << numBlocks.x << "x" << numBlocks.y << endl;
    cout << "Block size: " << threadsPerBlock.x << "x" << threadsPerBlock.y << endl;

    // Замер времени
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    matrixMulKernel << <numBlocks, threadsPerBlock >> > (d_A, d_B, d_C, N);
    cudaEventRecord(stop);

    // Проверка ошибок запуска ядра
    CHECK_CUDA_ERROR(cudaGetLastError());

    cudaEventSynchronize(stop);
    float elapsed_ms;
    cudaEventElapsedTime(&elapsed_ms, start, stop);
    float elapsed = elapsed_ms / 1000.0f;

    // Копирование результата обратно
    CHECK_CUDA_ERROR(cudaMemcpy(C.data(), d_C, size, cudaMemcpyDeviceToHost));

    // Запись результата
    write_matrix(fileResult, C, N);

    // Вывод
    cout << "Execution time: " << elapsed << " seconds" << endl;
    cout << "Task volume: " << (long long)N * N * N << " operations" << endl;

    // Очистка
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);

    return 0;
}