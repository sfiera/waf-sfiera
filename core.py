#!/usr/bin/env python

import sys
import textwrap
from waflib.Configure import conf
from waflib.Utils import to_list, unversioned_sys_platform

def dedent(s):
    return textwrap.dedent(s.strip("\n")).strip("\n")

def options(opt):
    opt.add_option(
            "-m", "--mode", action="store", default="dev", choices=["opt", "dev", "dbg"],
            help=dedent("""
                Select a set of compiler options.  Choices are "opt" (optimize for speed of the
                compiled executable), "dev" (optimize for speed of compilation process), and "dbg"
                (optimize for ability to debug).  [default: 'dev']
            """))

    opt.load("platform_%s" % unversioned_sys_platform())

def configure(cnf):
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
