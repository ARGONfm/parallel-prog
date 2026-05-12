#define MPICH_SKIP_MPICXX
#define OMPI_SKIP_MPICXX
#include <mpi.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <cstring>
#include <iomanip>

using namespace std;

void read_matrix(const char* filename, vector<vector<double> >& matrix, int& N) {
    ifstream file(filename);
    if (!file) {
        cerr << "Cannot open " << filename << endl;
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    file >> N;
    matrix.resize(N);
    for (int i = 0; i < N; ++i) {
        matrix[i].resize(N);
        for (int j = 0; j < N; ++j) {
            file >> matrix[i][j];
        }
    }
    file.close();
}

void write_matrix(const char* filename, const vector<vector<double> >& matrix, int N) {
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
    
    const char* fileA = argv[1];
    const char* fileB = argv[2];
    const char* fileResult = argv[3];
    
    int N = 0;
    vector<vector<double> > A, B;
    
    if (rank == 0) {
        read_matrix(fileA, A, N);
        read_matrix(fileB, B, N);
        cout << "Matrix size: " << N << "x" << N << endl;
        cout << "MPI processes: " << size << endl;
    }
    
    MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    int rows_per_proc = N / size;
    int remainder = N % size;
    
    vector<int> sendcounts(size), displs(size);
    int offset = 0;
    for (int i = 0; i < size; ++i) {
        sendcounts[i] = (i < remainder) ? rows_per_proc + 1 : rows_per_proc;
        displs[i] = offset;
        offset += sendcounts[i];
    }
    
    int local_rows = sendcounts[rank];
    
    vector<vector<double> > local_A(local_rows, vector<double>(N));
    vector<vector<double> > local_C(local_rows, vector<double>(N, 0.0));
    vector<vector<double> > B_full(N, vector<double>(N));
    
    if (rank == 0) {
        for (int i = 1; i < size; ++i) {
            for (int r = 0; r < sendcounts[i]; ++r) {
                MPI_Send(&A[displs[i] + r][0], N, MPI_DOUBLE, i, 0, MPI_COMM_WORLD);
            }
        }
        for (int r = 0; r < local_rows; ++r) {
            copy(A[displs[0] + r].begin(), A[displs[0] + r].end(), local_A[r].begin());
        }
        for (int i = 0; i < N; ++i) {
            MPI_Bcast(&B[i][0], N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        }
        B_full = B;
    } else {
        for (int r = 0; r < local_rows; ++r) {
            MPI_Recv(&local_A[r][0], N, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }
        for (int i = 0; i < N; ++i) {
            MPI_Bcast(&B_full[i][0], N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        }
    }
    
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();
    
    for (int i = 0; i < local_rows; ++i) {
        for (int k = 0; k < N; ++k) {
            double aik = local_A[i][k];
            for (int j = 0; j < N; ++j) {
                local_C[i][j] += aik * B_full[k][j];
            }
        }
    }
    
    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();
    double local_time = end_time - start_time;
    
    if (rank == 0) {
        vector<vector<double> > full_C(N, vector<double>(N));
        
        for (int r = 0; r < local_rows; ++r) {
            copy(local_C[r].begin(), local_C[r].end(), full_C[displs[0] + r].begin());
        }
        
        for (int i = 1; i < size; ++i) {
            vector<vector<double> > temp_C(sendcounts[i], vector<double>(N));
            for (int r = 0; r < sendcounts[i]; ++r) {
                MPI_Recv(&temp_C[r][0], N, MPI_DOUBLE, i, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }
            for (int r = 0; r < sendcounts[i]; ++r) {
                copy(temp_C[r].begin(), temp_C[r].end(), full_C[displs[i] + r].begin());
            }
        }
        
        write_matrix(fileResult, full_C, N);
        
        double max_time;
        MPI_Reduce(&local_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
        
        long long volume = (long long)N * N * N;
        cout << "Execution time: " << max_time << " seconds" << endl;
        cout << "Task volume: " << volume << " operations" << endl;
        cout << "Matrix size: " << N << "x" << N << endl;
        cout << "MPI processes: " << size << endl;
    } else {
        for (int r = 0; r < local_rows; ++r) {
            MPI_Send(&local_C[r][0], N, MPI_DOUBLE, 0, 1, MPI_COMM_WORLD);
        }
        MPI_Reduce(&local_time, NULL, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    }
    
    MPI_Finalize();
    return 0;
}