from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

import os

class xdiffRecipe(ConanFile):
    name = "xdiff"
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
    exports_sources = "CMakeLists.txt", "xdiff.def", "xdiff.rc"

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
        # unnecessary for the CMakeLists approach, where the test, tools, and man folders are NOT used
        if self.settings.os == "Windows":
            if self.options.shared:
                version_array = self.version.split(".")
                replace_in_file(self, os.path.join(self.source_folder, "xdiff.rc"),
                                "#define RC_VER_MAJOR", f"#define RC_VER_MAJOR {version_array[0]}")
                replace_in_file(self, os.path.join(self.source_folder, "xdiff.rc"),
                                "#define RC_VER_MINOR",
                                f"#define RC_VER_MINOR {version_array[1] if len(version_array) > 1 else 0}")
                replace_in_file(self, os.path.join(self.source_folder, "xdiff.rc"),
                                "#define RC_VER_BUILD",
                                f"#define RC_VER_BUILD {version_array[2] if len(version_array) > 2 else 0}")
                replace_in_file(self, os.path.join(self.source_folder, "xdiff.rc"),
                                "#define RC_VER_OTHER",
                                f"#define RC_VER_OTHER {version_array[3] if len(version_array) > 3 else 0}")
        else:
            replace_in_file(self, os.path.join(self.source_folder, "Makefile.am"),
                "SUBDIRS = . xdiff test tools man",
                "SUBDIRS = . xdiff")

            replace_in_file(self, os.path.join(self.source_folder, "configure.in"),
                "AC_OUTPUT(Makefile xdiff/Makefile test/Makefile tools/Makefile man/Makefile)",
                "AC_OUTPUT(Makefile xdiff/Makefile)")

            if self.options.shared:

                # there is not (yet?) a clear relationship between xdiff versions/releases and the
                # libtool scheme of current:revision:age . therefore, a mapping is used with the
                # expectation that the rate of revisions is so infrequent as to permit manual upkeep

                ld_version = None
                if self.version == "0.23":
                    ld_version = "0:23:0"

                if ld_version:
                    search_string = "lib_LTLIBRARIES = libxdiff.la"
                    replace_string = f"{search_string}%slibxdiff_la_LDFLAGS = -version-info {ld_version}" % os.linesep
                    replace_in_file(self, os.path.join(self.source_folder, "xdiff", "Makefile.am"),
                                    search_string, replace_string)
                else:
                    raise ConanException(f"Package build cannot proceed because version({self.version}) lacks a mapping to the current:revision:age model. "
                                        "Maintainer action required to correct this circumstance.")

    def build(self):
        self._patch_sources_autotools()
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
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

