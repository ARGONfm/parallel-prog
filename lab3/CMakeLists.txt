cmake_minimum_required(VERSION 3.10)
project(MatrixMult_Lab3_MPI)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пути к Microsoft MPI (после установки через winget)
set(MSMPI_INC "C:/Program Files (x86)/Microsoft SDKs/MPI/Include")
set(MSMPI_LIB "C:/Program Files (x86)/Microsoft SDKs/MPI/Lib/x64")

# Проверяем, существуют ли пути
if(EXISTS ${MSMPI_INC} AND EXISTS ${MSMPI_LIB})
    message(STATUS "Microsoft MPI found")
    add_executable(matrix_mpi matrix_mpi.cpp)
    target_include_directories(matrix_mpi PRIVATE ${MSMPI_INC})
    target_link_directories(matrix_mpi PRIVATE ${MSMPI_LIB})
    target_link_libraries(matrix_mpi PRIVATE msmpi)
else()
    message(FATAL_ERROR "Microsoft MPI not found! Please install Microsoft MPI.")
endif()

if(MSVC)
    set_property(TARGET matrix_mpi PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()