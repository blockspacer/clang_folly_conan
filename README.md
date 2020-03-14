# About

folly patched to support clang, fixes https://github.com/facebook/folly/issues/976

NOTE: required cmake definitions:

```bash
        cmake.definitions["BUILD_STATIC_LIBS"]="ON"
        cmake.definitions["BUILD_SHARED_LIBS"]="OFF"
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"]="ON"
        cmake.definitions["FOLLY_USE_JEMALLOC"]="OFF"
        cmake.definitions["CMAKE_CXX_FLAGS"]="-Wno-error=unused-parameter"
        cmake.definitions["FOLLY_CXX_FLAGS"]="-Wno-error=unused-parameter"
        cmake.definitions["BUILD_TESTS"]="OFF"
        cmake.definitions["USE_CMAKE_GOOGLE_TEST_INTEGRATION"]="OFF"
```

Based on https://github.com/bincrafters/conan-folly/blob/testing/2019.09.02/build.py

## Docker build with `--no-cache`

```bash
export MY_IP=$(ip route get 8.8.8.8 | sed -n '/src/{s/.*src *\([^ ]*\).*/\1/p;q}')
sudo -E docker build \
    --build-arg PKG_NAME=clang_folly_conan/v2019.01.14.00 \
    --build-arg PKG_CHANNEL=conan/stable \
    --build-arg PKG_UPLOAD_NAME=clang_folly_conan/v2019.01.14.00@conan/stable \
    --build-arg CONAN_EXTRA_REPOS="conan-local http://$MY_IP:8081/artifactory/api/conan/conan False" \
    --build-arg CONAN_EXTRA_REPOS_USER="user -p password1 -r conan-local admin" \
    --build-arg CONAN_UPLOAD="conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force" \
    --build-arg BUILD_TYPE=Debug \
    -f clang_folly_conan_source.Dockerfile --tag clang_folly_conan_repoadd_source_install . --no-cache

sudo -E docker build \
    --build-arg PKG_NAME=clang_folly_conan/v2019.01.14.00 \
    --build-arg PKG_CHANNEL=conan/stable \
    --build-arg PKG_UPLOAD_NAME=clang_folly_conan/v2019.01.14.00@conan/stable \
    --build-arg CONAN_EXTRA_REPOS="conan-local http://$MY_IP:8081/artifactory/api/conan/conan False" \
    --build-arg CONAN_EXTRA_REPOS_USER="user -p password1 -r conan-local admin" \
    --build-arg CONAN_UPLOAD="conan upload --all -r=conan-local -c --retry 3 --retry-wait 10 --force" \
    --build-arg BUILD_TYPE=Debug \
    -f clang_folly_conan_build.Dockerfile --tag clang_folly_conan_build_package_export_test_upload . --no-cache

# OPTIONAL: clear unused data
sudo -E docker rmi clang_folly_conan_*
```

## How to run single command in container using bash with gdb support

```bash
# about gdb support https://stackoverflow.com/a/46676907
docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --rm --entrypoint="/bin/bash" -v "$PWD":/home/u/project_copy -w /home/u/project_copy -p 50051:50051 --name DEV_clang_folly_conan clang_folly_conan -c pwd
```

## Local build

```bash
export CC=clang-6.0
export CXX=clang++-6.0

$CC --version
$CXX --version

conan remote add conan-center https://api.bintray.com/conan/conan/conan-center False

export PKG_NAME=clang_folly_conan/v2019.01.14.00@conan/stable

(CONAN_REVISIONS_ENABLED=1 \
    conan remove --force $PKG_NAME || true)

CONAN_REVISIONS_ENABLED=1 \
    CONAN_VERBOSE_TRACEBACK=1 \
    CONAN_PRINT_RUN_COMMANDS=1 \
    CONAN_LOGGING_LEVEL=10 \
    GIT_SSL_NO_VERIFY=true \
    conan create . conan/stable -s build_type=Debug --profile clang --build missing -o openssl:shared=True

CONAN_REVISIONS_ENABLED=1 \
    CONAN_VERBOSE_TRACEBACK=1 \
    CONAN_PRINT_RUN_COMMANDS=1 \
    CONAN_LOGGING_LEVEL=10 \
    conan upload $PKG_NAME --all -r=conan-local -c --retry 3 --retry-wait 10 --force
```

### License(s) for packaged software:

    ~/.conan/data/<pkg_name>/<pkg_version>/bincrafters/package/<random_package_id>/license/<LICENSE_FILES_HERE>

*Note :   The most common filenames for OSS licenses are `LICENSE` AND `COPYING` without file extensions.*
