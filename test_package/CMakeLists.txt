project(test_package)
cmake_minimum_required(VERSION 2.8.11)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/build/") # for conan

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR}/)
  include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
  include(${CMAKE_BINARY_DIR}/conan_paths.cmake OPTIONAL)
  conan_basic_setup(
    # prevent conan_basic_setup from resetting cmake variables
    TARGETS
    KEEP_RPATHS
    # see https://github.com/conan-io/conan/issues/6012
    NO_OUTPUT_DIRS
  )
else()
  message (FATAL_ERROR "must use conan")
endif()

#if(NOT TARGET CONAN_PKG::folly)
#  message(FATAL_ERROR "Use folly from conan")
#endif()

find_package(Threads REQUIRED)

# see https://github.com/civetweb/civetweb/blob/master/cmake/FindLibDl.cmake
find_path(LIBDL_INCLUDE_DIRS
  NAMES dlfcn.h
  PATHS ${LIBDL_ROOT}/include/
)
find_library(LIBDL_LIBRARIES dl)
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(LibDl DEFAULT_MSG LIBDL_LIBRARIES LIBDL_INCLUDE_DIRS)
mark_as_advanced(LIBDL_INCLUDE_DIRS LIBDL_LIBRARIES)

if(LIBDL_FOUND)
    if(NOT TARGET LIBDL::LIBDL)
      add_library(LIBDL::LIBDL UNKNOWN IMPORTED)
      set_target_properties(LIBDL::LIBDL PROPERTIES
        IMPORTED_LOCATION "${LIBDL_LIBRARIES}"
        INTERFACE_INCLUDE_DIRECTORIES "${LIBDL_INCLUDE_DIRS}")
    endif()
endif()

# see https://github.com/civetweb/civetweb/blob/master/cmake/FindLibM.cmake
find_path(LIBM_INCLUDE_DIRS
  NAMES math.h
  PATHS /usr/include /usr/local/include /usr/local/bic/include
  NO_DEFAULT_PATH
)
find_library(LIBM_LIBRARIES m)
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(LibM DEFAULT_MSG LIBM_LIBRARIES LIBM_INCLUDE_DIRS)
mark_as_advanced(LIBM_INCLUDE_DIRS LIBM_LIBRARIES)

if(LIBM_FOUND)
    if(NOT TARGET LIBM::LIBM)
      add_library(LIBM::LIBM UNKNOWN IMPORTED)
      set_target_properties(LIBM::LIBM PROPERTIES
        IMPORTED_LOCATION "${LIBM_LIBRARIES}"
        INTERFACE_INCLUDE_DIRECTORIES "${LIBM_INCLUDE_DIRS}")
    endif()
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME}
    LIBDL::LIBDL
    LIBM::LIBM
    Threads::Threads
    #
    CONAN_PKG::clang_folly_conan
    CONAN_PKG::boost
    CONAN_PKG::double-conversion
    CONAN_PKG::glog
    CONAN_PKG::libevent
    CONAN_PKG::lz4
    CONAN_PKG::openssl
    CONAN_PKG::lzma
    CONAN_PKG::zstd
    CONAN_PKG::snappy
    CONAN_PKG::libsodium
    CONAN_PKG::libdwarf
    CONAN_PKG::bzip2
    CONAN_PKG::gflags
    CONAN_PKG::libunwind
    #CONAN_PKG::OpenSSL
    CONAN_PKG::libelf
    CONAN_PKG::zlib
    CONAN_PKG::xz_utils
)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)

set_target_properties( ${PROJECT_NAME} PROPERTIES
  OUTPUT_NAME ${PROJECT_NAME}
  CXX_STANDARD 17
  CXX_EXTENSIONS OFF
  CMAKE_CXX_STANDARD_REQUIRED ON
  RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib )
