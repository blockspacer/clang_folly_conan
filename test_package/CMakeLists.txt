project(test_package)
cmake_minimum_required(VERSION 2.8.11)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

#if(NOT TARGET CONAN_PKG::folly)
#  message(FATAL_ERROR "Use folly from conan")
#endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME}
    #CONAN_PKG::folly
    #${CONAN_LIBS}
    #follybenchmark
    folly
    boost_wave
    boost_container
    boost_contract
    boost_exception
    boost_graph
    boost_iostreams
    boost_locale
    boost_log
    boost_program_options
    boost_random
    boost_regex
    boost_serialization
    boost_wserialization
    boost_coroutine
    boost_fiber
    boost_context
    boost_timer
    boost_thread
    boost_chrono
    boost_date_time
    boost_atomic
    boost_filesystem
    boost_system
    boost_type_erasure
    boost_log_setup
    boost_math_c99
    boost_math_c99f
    boost_math_c99l
    boost_math_tr1
    boost_math_tr1f
    boost_math_tr1l
    boost_stacktrace_addr2line
    boost_stacktrace_basic
    boost_stacktrace_noop
    boost_unit_test_framework
    double-conversion
    glog
    event
    event_core
    event_extra
    event_openssl
    event_pthreads
    rt
    lz4
    zstd
    snappy
    sodium
    dwarf
    bz2
    gflags_nothreads_debug
    m
    unwind
    unwind-coredump
    unwind-generic
    unwind-ptrace
    unwind-setjmp
    unwind-x86_64
    ssl
    crypto
    dl
    pthread
    elf
    z
    lzma
    iberty
)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)