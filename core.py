#!/usr/bin/env python

import sys
import textwrap
from waflib.Configure import conf
from waflib.Utils import to_list, unversioned_sys_platform

def dedent(s):
    return textwrap.dedent(s.strip("\n")).strip("\n")

def options(opt):
    opt.add_option(
            "-m", "--mode", action="store", default="opt", choices=["opt", "dev", "dbg"],
            help=dedent("""
                Select a set of compiler options.  Choices are "opt" (optimize for speed of the
                compiled executable), "dev" (optimize for speed of compilation process), and "dbg"
                (optimize for ability to debug).  [default: 'opt']
            """))

    opt.load("platform_%s" % unversioned_sys_platform())

def configure(cnf):
    if not hasattr(cnf, "c_std"):
        cnf.c_std = "c99"
    if cnf.c_std == "c89":
        cnf.env.append_unique("CFLAGS", ["-std=c89"])
    elif cnf.c_std == "c99":
        cnf.env.append_unique("CFLAGS", ["-std=c99"])

    if not hasattr(cnf, "cxx_std"):
        cnf.cxx_std = "c++98"
    if cnf.cxx_std == "c++11":
        cnf.env.append_unique("CXXFLAGS", ["-std=c++11", "-stdlib=libc++"])
        cnf.env.append_unique("LIB", "c++")
    elif cnf.cxx_std == "c++98":
        cnf.env.append_unique("CXXFLAGS", ["-std=c++98"])

    if cnf.options.mode == "opt":
        cnf.env.append_unique("CFLAGS", ["-Os", "-DNDEBUG"])
        cnf.env.append_unique("CXXFLAGS", ["-Os", "-DNDEBUG"])
    elif cnf.options.mode == "dev":
        pass
    elif cnf.options.mode == "dbg":
        cnf.env.append_unique("CFLAGS", "-g")
        cnf.env.append_unique("CXXFLAGS", "-g")

    cnf.load("platform_%s" % unversioned_sys_platform())

@conf
def platform(ctx, target, platform, **kwds):
    target = ctx.get_tgen_by_name(target)
    if unversioned_sys_platform() not in to_list(platform):
        return
    for key, val in kwds.items():
        setattr(target, key, to_list(getattr(target, key, [])))
        getattr(target, key).extend(to_list(val))
