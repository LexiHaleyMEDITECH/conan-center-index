from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

import os

class xdiffRecipe(ConanFile):
    name = "xdiff"
    version = "0.23"
    package_type = "library"

    # Optional metadata
    author = "Lexi Haley (lhaley@meditech.com)"
    description = "A C library to create file differences/patches for both binary and text files."
    homepage = "http://www.xmailserver.org/xdiff-lib.html"
    license = "LGPL-2.1-or-later"
    topics = ("diff", "patch", "text", "binary")
    url = "https://github.com/conan-io/conan-center-index"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "xdiff.def"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self)
        else:
            basic_layout(self)

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.preprocessor_definitions["HAVE_WINCONFIG_H"] = None
            tc.generate()
        else:
            at_toolchain = AutotoolsToolchain(self)
            at_toolchain.generate()
    
    def _patch_sources_autotools(self):
        # moot for the CMakeLists approach, where the test, tools, and man folders are NOT used
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.am"),
            "SUBDIRS = . xdiff test tools man",
            "SUBDIRS = . xdiff")
        replace_in_file(self, os.path.join(self.source_folder, "configure.in"),
            "AC_OUTPUT(Makefile xdiff/Makefile test/Makefile tools/Makefile man/Makefile)",
            "AC_OUTPUT(Makefile xdiff/Makefile)")

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            self._patch_sources_autotools()
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["xdiff"]

