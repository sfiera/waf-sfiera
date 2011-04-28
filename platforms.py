#!/usr/bin/env python

from waflib.Utils import unversioned_sys_platform

def options(opt):
    opt.load("platform_%s" % unversioned_sys_platform())

def configure(cnf):
    cnf.load("platform_%s" % unversioned_sys_platform())
