#!/usr/bin/env python

import os
import textwrap
from waflib.TaskGen import before_method, extension, feature

def dedent(s):
    return textwrap.dedent(s.strip("\n")).strip("\n")

SDKS = {
    "10.4": {
        "CC": "gcc-4.0",
        "CXX": "g++-4.0",
        "LINK_CC": "gcc-4.0",
        "LINK_CXX": "g++-4.0",
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "UNIVERSAL_ARCHES": ["ppc", "i386", "x86_64"],
    },
    "10.5": {
        "CC": "gcc-4.2",
        "CXX": "g++-4.2",
        "LINK_CC": "gcc-4.2",
        "LINK_CXX": "g++-4.2",
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.5.sdk", "-mmacosx-version-min=10.5"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.5.sdk", "-mmacosx-version-min=10.5"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.5.sdk", "-mmacosx-version-min=10.5"],
        "UNIVERSAL_ARCHES": ["ppc", "i386", "x86_64"],
    },
    "10.6": {
        "CC": "gcc-4.2",
        "CXX": "g++-4.2",
        "LINK_CC": "gcc-4.2",
        "LINK_CXX": "g++-4.2",
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.6.sdk", "-mmacosx-version-min=10.6"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.6.sdk", "-mmacosx-version-min=10.6"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.6.sdk", "-mmacosx-version-min=10.6"],
        "UNIVERSAL_ARCHES": ["i386", "x86_64"],
    },
    "10.7": {
        "CC": "gcc-4.2",
        "CXX": "g++-4.2",
        "LINK_CC": "gcc-4.2",
        "LINK_CXX": "g++-4.2",
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.7.sdk", "-mmacosx-version-min=10.7"],
        "UNIVERSAL_ARCHES": ["i386", "x86_64"],
    },
}

ARCH = ["ppc", "i386", "x86_64"]

def options(opt):
    opt.add_option(
            "--sdk", action="store", default="10.4", choices=sorted(SDKS.keys()),
            help="Compile against this SDK on darwin.  [default: '10.4']")
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
def build_universal(self):
    self.env.ARCH = [a for a in self.bld.env["UNIVERSAL_ARCHES"] if a in ["ppc", "i386"]]
    if not self.env.ARCH:
        raise self.bld.errors.ConfigurationError(
                "%s can only be built 32-bit" % self.target)


@extension(".m")
def m_hook(self, node):
    "Bind the m file extension to the same rules as c"
    return self.create_compiled_task("c", node)
