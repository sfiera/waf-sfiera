#!/usr/bin/env python

from __future__ import with_statement
import fnmatch
import os
import subprocess
import tempfile
from waflib import Context
from waflib import Logs
from waflib.Build import BuildContext
from waflib.Utils import Timer
from waflib.Configure import conf

def options(opt):
    opt.add_option(
            "--test-filter", action="store", default="*", metavar="FILTER",
            help="run only tests matching this pattern")


class TestContext(BuildContext):
    """runs tests associated with the build"""

    cmd = "test"

    def __init__(self):
        super(TestContext, self).__init__()
        self.test_cases = {}

    def execute(self):
        super(TestContext, self).execute()
        log_path = os.path.join(Context.top_dir, Context.out_dir, "test.log")
        self.logger = Logs.make_logger(log_path, "test")

        test_cases = []
        cases = set(fnmatch.filter(self.test_cases.keys(), self.options.test_filter))
        if not cases:
            self.fatal("no tests found: %s\n" % pattern)
        for case in cases:
            test_cases.append(self.test_cases[case])
        test_cases.sort(key=lambda case: case.target)

        failures = 0
        for case in test_cases:
            self.start_msg("Testing %s" % case.target)
            case_time = Timer()
            with tempfile.NamedTemporaryFile() as log:
                try:
                    case.execute(self, log)
                    self.end_msg("passed (%s)" % case_time, "GREEN")
                except AssertionError as e:
                    self.to_log(str(e))
                    self.to_log(open(log.name).read())
                    self.end_msg("failed (%s)" % case_time, "RED")
                    failures += 1
        if failures == 1:
            self.fatal("1 test failed")
        elif failures > 1:
            self.fatal("%d tests failed" % failures)


class TestCase(object):

    def __init__(self, bld, target):
        self.target = target
        self.binary = bld.path.find_or_declare(target)

    def execute(self, tst, log):
        binary = tst.path.find_resource(self.target)
        process = subprocess.Popen([self.binary.abspath()], stdout=log, stderr=log)
        process.communicate()
        assert process.returncode == 0, "%s failed" % self.target


@conf
def test(bld, *args, **kwds):
    try:
        target = kwds["target"]
    except KeyError:
        raise bld.errors.ConfigurationError("must specify target")

    bld.program(*args, **kwds)
    if hasattr(bld, "test_cases"):
        bld.test_cases[target] = TestCase(bld, target)
