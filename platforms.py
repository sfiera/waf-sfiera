#!/usr/bin/env python

import sys
from waflib.Configure import conf
from waflib.Utils import to_list, unversioned_sys_platform

def options(opt):
    opt.load("platform_%s" % unversioned_sys_platform())

def configure(cnf):
    cnf.load("platform_%s" % unversioned_sys_platform())

@conf
def platform(ctx, target, platform, **kwds):
    target = ctx.get_tgen_by_name(target)
    if unversioned_sys_platform() not in to_list(platform):
        return
    for key, val in kwds.items():
        setattr(target, key, to_list(getattr(target, key, [])))
        getattr(target, key).extend(to_list(val))
