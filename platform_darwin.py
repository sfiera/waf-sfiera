#!/usr/bin/env python

import os
from waflib.TaskGen import extension

SDKS = {
    "10.4": {
        "CC": "gcc-4.0",
        "CXX": "g++-4.0",
        "LINK_CC": "gcc-4.0",
        "LINK_CXX": "g++-4.0",
        "CFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "CXXFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
        "LINKFLAGS": ["-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk", "-mmacosx-version-min=10.4"],
    },
}

def options(opt):
    opt.add_option(
            "--sdk", action="store", default="10.4", choices=sorted(SDKS.keys()),
            help="compile against this SDK on darwin")

def configure(cnf):
    cnf.env.update(SDKS[cnf.options.sdk])


@extension(".m")
def m_hook(self, node):
    "Bind the m file extension to the same rules as c"
    return self.create_compiled_task("c", node)
