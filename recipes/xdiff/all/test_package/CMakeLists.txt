cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(xdiff CONFIG REQUIRED)

add_executable(example src/example.c)
target_link_libraries(example xdiff::xdiff)

if(XDIFF_SHARED_BUILD)
    target_compile_definitions(example PRIVATE XDIFF_SHARED_LIB=1)
endif()