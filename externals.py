#!/usr/bin/env python

import os
from waflib import Context
from waflib.Utils import to_list

def external(ctx, exts):
    if not hasattr(ctx, "ext_dir"):
        ctx.ext_dir = ctx.path.find_dir("ext")
    for ext in to_list(exts):
        ctx.recurse(ctx.ext_dir.find_node(ext).abspath())

Context.Context.external = external
