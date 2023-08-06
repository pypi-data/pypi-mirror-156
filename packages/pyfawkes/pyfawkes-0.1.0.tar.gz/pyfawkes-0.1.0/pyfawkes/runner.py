from multiprocessing import Pool, TimeoutError
from collections import namedtuple
import inspect
import sys

import pytest
from _pytest.config import default_plugins


KILLED, SURVIVED, INCOMPETENT, TIMEOUT = "Killed", "Survived", "Incompetent", "Timeout"
Result = namedtuple("Result", ["state", "killer", "tests_run"])


def safe_getattr(obj, name):
    return object.__getattribute__(obj, name)


def inject_to(source, target):
    for imported_as, artefact in target.__dict__.copy().items():
        if inspect.ismodule(artefact):
            if safe_getattr(artefact, "__name__") == source.__name__:
                source.__file__ = artefact.__file__
                target.__dict__[imported_as] = source
        elif inspect.isclass(artefact) or inspect.isfunction(artefact):
            if safe_getattr(artefact, "__name__") in source.__dict__:
                target.__dict__[imported_as] = source.__dict__[safe_getattr(artefact, "__name__")]
        else:
            if imported_as in source.__dict__ and imported_as not in ["__builtins__", "__name__", "__doc__", "__file__"]:
                target.__dict__[imported_as] = source.__dict__[imported_as]


class PytestPyfawkesPlugin:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []
        self.errors = []

    def pytest_runtest_logreport(self, report):
        if report.skipped:
            self.skipped.append(report.nodeid)
        elif report.failed:
            if "TypeError" in report.longrepr.reprcrash.message:
                self.errors.append(TypeError(str(report.longrepr.reprcrash)))
            else:
                self.failed.append(report.nodeid)
        elif report.passed and report.when == "teardown" and report.nodeid not in self.failed:
            self.passed.append(report.nodeid)


def helper(tests):
    pyfawkes_plugin = PytestPyfawkesPlugin()
    pytest.main(args=tests + ["-x", "-p", "no:terminal"], plugins=list(default_plugins) + [pyfawkes_plugin])

    count = len(pyfawkes_plugin.passed) + len(pyfawkes_plugin.failed)
    if pyfawkes_plugin.errors:
        return Result(INCOMPETENT, "", 0)
    if pyfawkes_plugin.failed:
        return Result(KILLED, pyfawkes_plugin.failed[0], count)
    return Result(SURVIVED, "", count)


class PytestTestRunner:
    def __init__(self, tests):
        self.modules = set()
        self.tests = set()
        for test_module in tests:
            self.modules.add(test_module)
            self.tests.add(getattr(test_module, "__file__", test_module.__name__))

    def run(self, max_duration=None, mutant_module=None):
        if mutant_module is not None:
            sys.modules[mutant_module.__name__] = mutant_module
            for test_module in self.modules:
                inject_to(mutant_module, test_module)

        with Pool(processes=1) as pool:
            token = pool.apply_async(helper, args=(list(self.tests),))
            try:
                return token.get(timeout=max_duration)
            except TimeoutError:
                return Result(TIMEOUT, "", 0)
