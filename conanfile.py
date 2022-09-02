import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration

class FollyConan(ConanFile):
    name = "clang_folly_conan"
    version = "v2019.01.14.00"
    description = "An open-source C++ components library developed and used at Facebook"
    topics = ("conan", "folly", "facebook", "components", "core", "efficiency")
    #url = "https://github.com/bincrafters/conan-folly" # TODO
    #homepage = "https://github.com/facebook/folly" # TODO
    #license = "Apache-2.0" # TODO
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True,
        "*:shared": False,
        "openssl:shared": True
    }
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake"
    commit_hash = "67f61a811de7af0b87453fcc272aba4106c881e1"
    repo_url = "https://github.com/facebook/folly.git"

    # conan search double-conversion* -r=conan-center
    requires = (
        # patched to support "zlib/v1.2.11@conan/stable" with "openssl/1.1.1-stable@conan/stable"
        "boost/1.72.0@dev/stable",
        "double-conversion/3.1.1@bincrafters/stable",
#        "double-conversion/3.1.5@bincrafters/stable",
        "gflags/2.2.2@bincrafters/stable",
        "glog/0.4.0@bincrafters/stable",
        # patched to support "openssl/1.1.1-stable@conan/stable"
        "libevent/2.1.11@dev/stable",
#        "lz4/1.9.2",
        "lz4/1.8.3@bincrafters/stable",
#        "lz4/1.9.2@bincrafters/stable",
#        "openssl/1.0.2u@conan/stable",
#        "openssl/1.0.2u",
#        "openssl/1.1.1c",
        "openssl/1.1.1-stable@conan/stable",
        # patched to support "openssl/1.1.1-stable@conan/stable"
        # TODO: use self.requires("chromium_zlib/master@conan/stable")
        "zlib/v1.2.11@conan/stable",
        #"zlib/1.2.11@conan/stable",
        "lzma/5.2.4@bincrafters/stable",
#        "zstd/1.4.3@conan/stable",
#        "zstd/1.4.3",
        "zstd/1.3.8@bincrafters/stable",
        "snappy/1.1.7@bincrafters/stable",
        "bzip2/1.0.8@dev/stable", # @conan/stable
        "libsodium/1.0.18@bincrafters/stable",
        "libelf/0.8.13@bincrafters/stable",
#        "xz_utils/5.2.4@conan-center/stable",
#        "libdwarf/20191104"
        "libdwarf/20190505@bincrafters/stable"
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
        elif self.settings.os == "Macos":
            del self.options.shared

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)

        # NOTE: our patched folly version requires clang
        #if self.settings.compiler != "apple-clang" and \
        #     self.settings.compiler != "clang" and \
        #     self.settings.compiler != "clang-cl":
        #    raise ConanInvalidConfiguration("Use clang")

        if self.settings.os == "Windows" and \
            self.settings.compiler == "Visual Studio" and \
            compiler_version < "15":
            raise ConanInvalidConfiguration("Folly could not be built by Visual Studio < 14")
        elif self.settings.os == "Windows" and \
            self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture")
        elif self.settings.os == "Windows" and \
             self.settings.compiler == "Visual Studio" and \
             "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Folly could not be build with runtime MT")
        elif self.settings.os == "Linux" and \
            self.settings.compiler == "clang" and \
            compiler_version < "6.0":
            raise ConanInvalidConfiguration("Folly could not be built by Clang < 6.0")
        elif self.settings.os == "Linux" and \
            self.settings.compiler == "gcc" and \
            compiler_version < "5":
            raise ConanInvalidConfiguration("Folly could not be built by GCC < 5")
        elif self.settings.os == "Macos" and \
             self.settings.compiler == "apple-clang" and \
             compiler_version < "8.0":
            raise ConanInvalidConfiguration("Folly could not be built by apple-clang < 8.0")

    def requirements(self):
        print('self.settings.compiler {}'.format(self.settings.compiler))

        # NOTE: our patched folly version requires clang
        #if self.settings.compiler != "apple-clang" and \
        #     self.settings.compiler != "clang" and \
        #     self.settings.compiler != "clang-cl":
        #    raise ConanInvalidConfiguration("Use clang")

        #if self.settings.os == "Linux" and \
        #   self.settings.compiler == "gcc":
        #    self.requires("libiberty/9.1.0")
        if self.settings.os == "Linux":
            self.requires("libiberty/9.1.0")

    def source(self):
        #tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        #extracted_dir = self.name + '-' + self.version
        #os.rename(extracted_dir, self._source_subfolder)
        self.run('git clone -b {} --progress --depth 100 --recursive --recurse-submodules {} {}'.format(self.version, self.repo_url, self._source_subfolder))
        #self.run('cd {} && ls -artlh && git reset --hard {} && git submodule init && git submodule update'.format(self._source_subfolder, self.commit_hash))

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.verbose = True

        cmake.definitions["BUILD_STATIC_LIBS"]="ON"
        cmake.definitions["BUILD_SHARED_LIBS"]="OFF"
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"]="ON"
        cmake.definitions["FOLLY_USE_JEMALLOC"]="OFF"
        cmake.definitions["CMAKE_CXX_FLAGS"]="-Wno-error=unused-parameter"
        cmake.definitions["FOLLY_CXX_FLAGS"]="-Wno-error=unused-parameter"
        cmake.definitions["BUILD_TESTS"]="OFF"
        cmake.definitions["USE_CMAKE_GOOGLE_TEST_INTEGRATION"]="OFF"

        cmake.configure()
        return cmake

    def build(self):
        with tools.vcvars(self.settings, only_diff=False): # https://github.com/conan-io/conan/issues/6577
            #tools.patch(base_path=self._source_subfolder, patch_file='0001-compiler-options.patch')
            tools.patch(base_path=self._source_subfolder, patch_file='0002-clang-cling-conan-support.patch')
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        with tools.vcvars(self.settings, only_diff=False): # https://github.com/conan-io/conan/issues/6577
            self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
            cmake = self._configure_cmake()
            cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
            # + ["folly"] # https://github.com/conan-io/conan/issues/2193

        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "m", "dl"])
            if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++":
                self.cpp_info.libs.append("atomic")
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])

        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
           Version(self.settings.compiler.version.value) == "6" and self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
           Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.libs.append("atomic")
