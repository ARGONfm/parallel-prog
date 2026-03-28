cmake_minimum_required(VERSION 3.10)
project(MatrixMult_Lab2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenMP REQUIRED)

add_executable(matrix_mult matrix_mult.cpp)

target_link_libraries(matrix_mult PRIVATE OpenMP::OpenMP_CXX)

if(MSVC)
    set_property(TARGET matrix_mult PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()