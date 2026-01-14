cmake_minimum_required(VERSION 3.15)
project(xdiff LANGUAGES C)

file(GLOB XDIFF_SRCS xdiff/*.c)

if (BUILD_SHARED_LIBS)
    if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
        list(APPEND XDIFF_SRCS xdiff.def xdiff.rc)
    endif()
    add_library(xdiff SHARED ${XDIFF_SRCS})
else()
    add_library(xdiff STATIC ${XDIFF_SRCS})
endif()

target_include_directories(xdiff PUBLIC .)
target_include_directories(xdiff PUBLIC xdiff)

set_target_properties(xdiff PROPERTIES PUBLIC_HEADER "xdiff/xdiff.h")
install(TARGETS xdiff)
