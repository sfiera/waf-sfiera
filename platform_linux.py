#!/usr/bin/env python


@feature("universal")
@before_method("process_source")
def build_universal(self):
    """Ignore universal feature."""


@feature("universal32")
@before_method("process_source")
def build_universal(self):
    """Ignore universal32 feature."""
