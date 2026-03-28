cmake_minimum_required(VERSION 3.10)
project(MatrixMult)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenMP REQUIRED)

add_executable(matrix_mult matrix_mult.cpp)

target_link_libraries(matrix_mult PRIVATE OpenMP::OpenMP_CXX)