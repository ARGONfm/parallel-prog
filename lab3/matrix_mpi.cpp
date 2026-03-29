#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <mpi.h>
#include <cmath>

using namespace std;

void read_matrix(const string& filename, vector<vector<double>>& matrix, int& N) {
    ifstream file(filename);
    if (!file) {
        cerr << "Cannot open " << filename << endl;
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    file >> N;
    matrix.resize(N, vector<double>(N));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            file >> matrix[i][j];
        }
    }
    file.close();
}

void write_matrix(const string& filename, const vector<vector<double>>& matrix, int N) {
    ofstream file(filename);
    if (!file) {
        cerr << "Cannot open " << filename << endl;
        return;
    }
    file << N << endl;
    file << fixed << setprecision(6);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            file << matrix[i][j] << " ";
        }
        file << endl;
    }
    file.close();
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 4) {
        if (rank == 0) {
            cerr << "Usage: " << argv[0] << " <matrixA> <matrixB> <result>" << endl;
        }
        MPI_Finalize();
        return 1;
    }

    string fileA = argv[1];
    string fileB = argv[2];
    string fileResult = argv[3];

    int N = 0;
    vector<vector<double>> A, B, C;

    // Только процесс 0 читает матрицы
    if (rank == 0) {
        read_matrix(fileA, A, N);
        read_matrix(fileB, B, N);

        // Проверка размера
        if (N != (int)B.size()) {
            cerr << "Matrix sizes do not match!" << endl;
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        cout << "Matrix size: " << N << "x" << N << endl;
        cout << "MPI processes: " << size << endl;
    }

    // Рассылаем размер N всем процессам
    MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Подготовка к распределению строк
    int rows_per_proc = N / size;
    int remainder = N % size;

    // Определяем, сколько строк получит каждый процесс
    vector<int> sendcounts(size), displs(size);
    int offset = 0;
    for (int i = 0; i < size; ++i) {
        sendcounts[i] = (i < remainder) ? rows_per_proc + 1 : rows_per_proc;
        displs[i] = offset;
        offset += sendcounts[i];
    }

    int local_rows = sendcounts[rank];

    // Локальные матрицы
    vector<vector<double>> local_A(local_rows, vector<double>(N));
    vector<vector<double>> local_C(local_rows, vector<double>(N, 0.0));

    // Матрица B (нужна всем)
    vector<vector<double>> B_full(N, vector<double>(N));

    if (rank == 0) {
        // Распределяем строки матрицы A по процессам
        for (int i = 1; i < size; ++i) {
            for (int r = 0; r < sendcounts[i]; ++r) {
                MPI_Send(A[displs[i] + r].data(), N, MPI_DOUBLE, i, 0, MPI_COMM_WORLD);
            }
        }
        // Копируем свою часть A
        for (int r = 0; r < local_rows; ++r) {
            copy(A[displs[0] + r].begin(), A[displs[0] + r].end(), local_A[r].begin());
        }

        // Рассылаем матрицу B всем процессам
        for (int i = 0; i < N; ++i) {
            MPI_Bcast(B[i].data(), N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        }

        // Копируем B для себя
        B_full = B;
    }
    else {
        // Принимаем свою часть A
        for (int r = 0; r < local_rows; ++r) {
            MPI_Recv(local_A[r].data(), N, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }

        // Принимаем матрицу B
        for (int i = 0; i < N; ++i) {
            MPI_Bcast(B_full[i].data(), N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        }
    }

    // Синхронизация перед замером времени
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    // Локальное умножение
    for (int i = 0; i < local_rows; ++i) {
        for (int k = 0; k < N; ++k) {
            double aik = local_A[i][k];
            for (int j = 0; j < N; ++j) {
                local_C[i][j] += aik * B_full[k][j];
            }
        }
    }

    // Синхронизация после вычислений
    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();
    double local_time = end_time - start_time;

    // Собираем результат на процессе 0
    vector<vector<double>> full_C;
    if (rank == 0) {
        full_C.resize(N, vector<double>(N));

        // Собираем свою часть
        for (int r = 0; r < local_rows; ++r) {
            copy(local_C[r].begin(), local_C[r].end(), full_C[displs[0] + r].begin());
        }

        // Собираем результаты от других процессов
        for (int i = 1; i < size; ++i) {
            vector<vector<double>> temp_C(sendcounts[i], vector<double>(N));
            for (int r = 0; r < sendcounts[i]; ++r) {
                MPI_Recv(temp_C[r].data(), N, MPI_DOUBLE, i, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }
            for (int r = 0; r < sendcounts[i]; ++r) {
                copy(temp_C[r].begin(), temp_C[r].end(), full_C[displs[i] + r].begin());
            }
        }

        // Запись результата
        write_matrix(fileResult, full_C, N);

        // Вывод статистики
        double max_time;
        MPI_Reduce(&local_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

        long long volume = static_cast<long long>(N) * N * N;
        cout << "Execution time: " << max_time << " seconds" << endl;
        cout << "Task volume: " << volume << " operations" << endl;
        cout << "Matrix size: " << N << "x" << N << endl;
        cout << "MPI processes: " << size << endl;
    }
    else {
        // Отправляем результаты процессу 0
        for (int r = 0; r < local_rows; ++r) {
            MPI_Send(local_C[r].data(), N, MPI_DOUBLE, 0, 1, MPI_COMM_WORLD);
        }

        // Участвуем в редукции времени
        MPI_Reduce(&local_time, NULL, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
}