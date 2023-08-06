from collections import defaultdict
from multiprocessing import Pool, TimeoutError
from random import seed
import argparse
import inspect
import sys
import types

import pytest
from pytest import ExitCode

from jitterbug import __version__ as version
from jitterbug.utils import timer, create_ast
from jitterbug.loader import load
from jitterbug.mutator import mutate

PASSED, FAILED, TIMEOUT = "Passed", "Failed", "Timeout"

def main():
    parser = argparse.ArgumentParser(description="Mutation testing tool for Python 3.x source code.", fromfile_prefix_chars="@")
    parser.add_argument("--version", "-v", action="version", version=f"Jitterbug {version}")
    parser.add_argument("--source", "-s", type=str, nargs="+", help="source module or package to mutate", required=True)
    parser.add_argument("--test", "-t", type=str, nargs="+", help="test class, test method, module or package with unit tests", required=True)
    parser.add_argument("--timeout-factor", "-f", type=float, default=5, help="max timeout factor")
    parser.add_argument("--prob", "-p", type=float, default=0.5, help="prob of mutating a node each run")
    parser.add_argument("--seed", type=int, help="random seed")
    args = parser.parse_args()

    if args.seed:
        seed(args.seed)

    run(args.source, args.test, args.timeout_factor, args.prob)


def run(sources, test_targets, timeout_factor, prob=0.5):
    tests = list(load(test_targets))
    s_tests = list(set(getattr(test, "__file__", test.__name__) for test in tests))
    score = defaultdict(int)

    print("Start mutation process:")
    print("  - sources: {}".format(", ".join(sources)))
    print("  - tests: {}".format(", ".join(test_targets)))
    with timer() as total:
        with timer() as standard:
            result = helper(s_tests)
        if result != PASSED:
            raise RuntimeError("Unmutated tests do not pass")

        print("Unmutated tests passed")
        print("Start mutants generation and execution:")

        max_duration = max(standard.duration, 1) * timeout_factor
        for target_module in load(sources, skip=tests):
            with open(target_module.__file__) as target_file:
                target_ast = create_ast(target_file.read())

            for index, site_mutation in enumerate(mutate(target_ast, prob=prob), start=1):
                print(f" - [#{index:>4}] {target_module.__name__}: ", end="")
                with site_mutation():
                    code = compile(target_ast, target_module.__name__, "exec")
                    mutant = types.ModuleType(target_module.__name__)
                    exec(code, mutant.__dict__)

                    sys.modules[mutant.__name__] = mutant
                    for test_module in tests:
                        inject_to(mutant, test_module)

                    with timer() as experiment, Pool(processes=1) as pool:
                        token = pool.apply_async(helper, args=(s_tests,))
                        try:
                            result = token.get(timeout=max_duration)
                        except TimeoutError:
                            result = TIMEOUT
                    print(f"[{experiment.duration:.5f}s] {result}")
                    score[result] += 1

    # Report results.
    all_mutants = sum(score.values())
    percentage = ((score[PASSED] + score[TIMEOUT]) / all_mutants) if all_mutants else 0

    print(f"Jitter score [{total.duration:.5f}s]: {percentage:.1%}")

    if all_mutants:
        print(f"  - Passed:  {score[PASSED]} / {all_mutants} ({score[PASSED] / all_mutants:.1%}%)")
        print(f"  - Failed:  {score[FAILED]} / {all_mutants} ({score[FAILED] / all_mutants:.1%}%)")
        print(f"  - Timeout: {score[TIMEOUT]} / {all_mutants} ({score[TIMEOUT] / all_mutants:.1%})")


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


def helper(tests):
    result = pytest.main(args=tests + ["-x", "-p", "no:terminal"])
    if result == ExitCode.OK:
        return PASSED

    # ExitCode.INTERNAL_ERROR
    # ExitCode.NO_TESTS_COLLECTED
    # ExitCode.TESTS_FAILED
    # ExitCode.INTERRUPTED
    # ExitCode.USAGE_ERROR
    return FAILED
