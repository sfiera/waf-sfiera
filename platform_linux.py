#!/usr/bin/env python

from waflib.TaskGen import before_method, feature


COMPILERS = {
    "gcc": {
        "CC": "gcc-4.4",
        "CXX": "g++-4.4",
        "LINK_CC": "gcc-4.4",
        "LINK_CXX": "g++-4.4",
    },
    "clang": {
        "CC": "clang",
        "CXX": "clang++",
        "LINK_CC": "clang",
        "LINK_CXX": "clang++",
    },
}

def options(opt):
    if not hasattr(opt, "default_compiler"):
        raise opt.errors.ConfigurationError("must set default_compiler")
    opt.add_option(
            "--compiler", action="store", default=opt.default_compiler, choices=["clang", "gcc"],
            help="Use this compiler on linux.  [default: %r]" % opt.default_compiler)


def configure(cnf):
    if cnf.options.compiler not in COMPILERS:
        raise cnf.errors.ConfigurationError("cannot compile with %s" % cnf.options.compiler)
    for key, val in COMPILERS[cnf.options.compiler].items():
        if isinstance(val, list):
            cnf.env.append_unique(key, val)
        else:
            cnf.env[key] = val


@feature("universal")
@before_method("process_source")
def build_universal(self):
    """Ignore universal feature."""


@feature("universal32")
@before_method("process_source")
def build_universal(self):
    """Ignore universal32 feature."""
