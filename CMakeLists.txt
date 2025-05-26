cmake_minimum_required(VERSION 3.10)
project(AnomSched)

set(CMAKE_CXX_STANDARD 17)

add_executable(AnomSched
    src/main.cpp
    src/scheduler.cpp
    src/logger.cpp
)

target_include_directories(AnomSched PRIVATE src)
