#!/usr/bin/env python

import os
import textwrap
from waflib.TaskGen import before_method, extension, feature

def dedent(s):
    return textwrap.dedent(s.strip("\n")).strip("\n")

SDKS = {
    "10.4": {
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "UNIVERSAL_ARCHES": ["ppc", "i386", "x86_64"],
    },
    "10.5": {
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.5.sdk", "-mmacosx-version-min=10.5"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.5.sdk", "-mmacosx-version-min=10.5"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.5.sdk", "-mmacosx-version-min=10.5"],
        "UNIVERSAL_ARCHES": ["ppc", "i386", "x86_64"],
    },
    "10.6": {
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.6.sdk", "-mmacosx-version-min=10.6"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.6.sdk", "-mmacosx-version-min=10.6"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.6.sdk", "-mmacosx-version-min=10.6"],
        "UNIVERSAL_ARCHES": ["i386", "x86_64"],
    },
    "10.7": {
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "UNIVERSAL_ARCHES": ["i386", "x86_64"],
    },
    "10.7-clang": {
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "UNIVERSAL_ARCHES": ["i386", "x86_64"],
    },
}

COMPILERS = {
    ("10.4", "gcc"): {
        "CC": "gcc-4.0",
        "CXX": "g++-4.0",
        "LINK_CC": "gcc-4.0",
        "LINK_CXX": "g++-4.0",
    },
    ("10.5", "gcc"): {
        "CC": "gcc-4.2",
        "CXX": "g++-4.2",
        "LINK_CC": "gcc-4.2",
        "LINK_CXX": "g++-4.2",
    },
    ("10.6", "gcc"): {
        "CC": "gcc-4.2",
        "CXX": "g++-4.2",
        "LINK_CC": "gcc-4.2",
        "LINK_CXX": "g++-4.2",
    },
    ("10.7", "gcc"): {
        "CC": "llvm-gcc-4.2",
        "CXX": "llvm-g++-4.2",
        "LINK_CC": "llvm-gcc-4.2",
        "LINK_CXX": "llvm-g++-4.2",
    },
    ("10.6", "clang"): {
        "CC": "clang",
        "CXX": "clang++",
        "LINK_CC": "clang",
        "LINK_CXX": "clang++",
    },
    ("10.7", "clang"): {
        "CC": "clang",
        "CXX": "clang++",
        "LINK_CC": "clang",
        "LINK_CXX": "clang++",
    },
}

ARCH = ["ppc", "i386", "x86_64"]

def options(opt):
    if not hasattr(opt, "default_sdk"):
        raise opt.errors.ConfigurationError("must set default_sdk")
    if not hasattr(opt, "default_compiler"):
        raise opt.errors.ConfigurationError("must set default_compiler")
    opt.add_option(
            "--sdk", action="store", default=opt.default_sdk, choices=sorted(SDKS.keys()),
            help="Compile against this SDK on darwin.  [default: %r]" % opt.default_sdk)
    opt.add_option(
            "--compiler", action="store", default=opt.default_compiler, choices=["clang", "gcc"],
            help="Use this compiler on darwin.  [default: %r]" % opt.default_compiler)
    opt.add_option(
            "--arch", action="append", default=[], choices=ARCH,
            help=dedent("""
                Append to the list of architectures to build.  Individual targets may not build
                on the specified architecture.  [default: SDK-dependent]
            """))

def configure(cnf):
    for key, val in SDKS[cnf.options.sdk].items():
        if isinstance(val, list):
            cnf.env.append_unique(key, val)
        else:
            cnf.env[key] = val

    if (cnf.options.sdk, cnf.options.compiler) not in COMPILERS:
        raise cnf.errors.ConfigurationError(
                "cannot compile with %s on %s" % (cnf.options.compiler, cnf.options.sdk))
    for key, val in COMPILERS[cnf.options.sdk, cnf.options.compiler].items():
        if isinstance(val, list):
            cnf.env.append_unique(key, val)
        else:
            cnf.env[key] = val

    if cnf.options.arch:
        # If any arch passed via --arch cannot be built against the
        # selected SDK, raise an error about the first such arch
        # encountered.
        bad_arches = [a for a in cnf.options.arch if a not in cnf.env["UNIVERSAL_ARCHES"]]
        if bad_arches:
            raise cnf.errors.ConfigurationError(
                    "cannot build %s on %s" % (bad_arches.pop(0), cnf.options.sdk))
        cnf.env["UNIVERSAL_ARCHES"] = cnf.options.arch


@feature("universal")
@before_method("process_source")
def build_universal(self):
    self.env.ARCH = self.bld.env["UNIVERSAL_ARCHES"]


@feature("universal32")
@before_method("process_source")
def build_universal32(self):
    self.env.ARCH = [a for a in self.bld.env["UNIVERSAL_ARCHES"] if a in ["ppc", "i386"]]
    if not self.env.ARCH:
        raise self.bld.errors.ConfigurationError(
                "%s can only be built 32-bit" % self.target)


@extension(".m")
def m_hook(self, node):
    "Bind the m file extension to the same rules as c"
    return self.create_compiled_task("c", node)
