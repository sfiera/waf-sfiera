#!/usr/bin/env python

import glob
import os
import textwrap
from waflib.TaskGen import before_method, extension, feature

def dedent(s):
    return textwrap.dedent(s.strip("\n")).strip("\n")

SDK_ROOT = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs"

SDKS = {}
for sdk in glob.glob(SDK_ROOT + "/MacOSX10.*.sdk"):
    basename = os.path.basename(sdk)
    try:
        version = int(basename[9:-4])
    except ValueError:
        continue
    flags = [
        "-isysroot", SDK_ROOT + "/MacOSX10.%d.sdk" % version,
    ]
    SDKS[version] = {
        "CFLAGS": flags,
        "CXXFLAGS": flags,
        "LINKFLAGS": flags,
        "UNIVERSAL_ARCHES": ["i386", "x86_64"],
    }

LATEST_SDK = "10.%d" % max(SDKS)
MAC_TARGETS = ["10.%d" % x for x in xrange(max(SDKS), 4, -1)]
SDKS = {"10.%d" % k: v for k, v in sorted(SDKS.iteritems())}

CLANG = {
    "CC": "clang",
    "CXX": "clang++",
    "LINK_CC": "clang",
    "LINK_CXX": "clang++",
}

ARCH = ["i386", "x86_64"]

def options(opt):
    if not hasattr(opt, "default_sdk"):
        opt.default_sdk = LATEST_SDK
    if not hasattr(opt, "mac_target"):
        raise opt.errors.ConfigurationError("must set mac_target")
    elif opt.mac_target not in MAC_TARGETS:
        raise opt.errors.ConfigurationError("mac_target must be one of %r" % MAC_TARGETS)

    if hasattr(opt, "platform_darwin_initialized"):
        return
    else:
        opt.platform_darwin_initialized = True

    opt.add_option(
            "--sdk", action="store", default=opt.default_sdk, choices=sorted(SDKS.keys()),
            help="Compile against this SDK on darwin.  [default: %r]" % opt.default_sdk)
    opt.add_option(
            "--arch", action="append", default=[], choices=ARCH,
            help=dedent("""
                Append to the list of architectures to build.  Individual targets may not build
                on the specified architecture.  [default: x86_64, i386]
            """))

def configure(cnf):
    for key in ["CFLAGS", "CXXFLAGS", "LINKFLAGS"]:
        cnf.env.append_unique(key, "-mmacosx-version-min=%s" % cnf.mac_target)

    for key, val in SDKS[cnf.options.sdk].items():
        if isinstance(val, list):
            cnf.env.append_unique(key, val)
        else:
            cnf.env[key] = val

    for key, val in CLANG.items():
        if isinstance(val, list):
            cnf.env.append_unique(key, val)
        else:
            cnf.env[key] = val

    if cnf.options.arch:
        cnf.env["UNIVERSAL_ARCHES"] = cnf.options.arch


@feature("universal")
@before_method("process_source")
def build_universal(self):
    self.env.ARCH = self.bld.env["UNIVERSAL_ARCHES"]


@extension(".m")
def m_hook(self, node):
    "Bind the m file extension to the same rules as c"
    return self.create_compiled_task("c", node)


@extension(".mm")
def m_hook(self, node):
    "Bind the mm file extension to the same rules as cxx"
    return self.create_compiled_task("cxx", node)
