from collections import defaultdict
import argparse
import types

from pyfawkes import __version__ as version
from pyfawkes.utils import timer, create_ast
from pyfawkes.loader import load
from pyfawkes.runner import PytestTestRunner, KILLED, SURVIVED, INCOMPETENT, TIMEOUT
from pyfawkes.mutator import Mutator


def main():
    parser = argparse.ArgumentParser(description="Mutation testing tool for Python 3.x source code.", fromfile_prefix_chars="@")
    parser.add_argument("--version", "-v", action="version", version=f"PyFawkes {version}")
    parser.add_argument("--source", "-s", type=str, nargs="+", help="source module or package to mutate")
    parser.add_argument("--test", "-t", type=str, nargs="+", help="test class, test method, module or package with unit tests")
    parser.add_argument("--timeout-factor", "-f", type=float, default=5, help="max timeout factor")
    parser.add_argument("--enable", "-e", type=str, nargs="+", help="use only selected operators", metavar="OPERATOR")
    parser.add_argument("--disable", "-d", type=str, nargs="+", default=[], help="disable selected operators", metavar="OPERATOR")
    parser.add_argument("--list-operators", "-l", action="store_true", help="list available operators")
    args = parser.parse_args()

    if args.list_operators:
        list_operators()
    elif args.source and args.test:
        operators_abbreviations = set(args.enable if args.enable else Mutator.all_methods)
        operators_abbreviations -= set(args.disable)
        run(
            args.source,
            args.test,
            operators_abbreviations,
            args.timeout_factor,
        )
    else:
        parser.print_usage()


def list_operators():
    operators = dict()
    for attr in dir(Mutator):
        method = getattr(Mutator, attr)
        if hasattr(method, "abbr"):
            operators[method.abbr] = method.name

    print("Operators:")
    for abbr, name in sorted(operators.items()):
        print(f"  {abbr:3} - {name}")


def run(sources, test_targets, operator_abbreviations, timeout_factor):
    tests = list(load(test_targets))
    test_runner = PytestTestRunner(tests)
    score = defaultdict(int)
    mutator = Mutator(operator_abbreviations)

    print("Start mutation process:")
    print("  - sources: {}".format(", ".join(sources)))
    print("  - tests: {}".format(", ".join(test_targets)))
    with timer() as total:
        with timer() as standard:
            result = test_runner.run()
        if result.state != SURVIVED:
            raise RuntimeError("Unmutated tests do not pass")

        print(f"{result.tests_run} tests passed")
        print("Start mutants generation and execution:")

        max_duration = max(standard.duration, 1) * timeout_factor
        for target_module in load(sources, skip=tests):
            with open(target_module.__file__) as target_file:
                target_ast = create_ast(target_file.read())

            for index, site_mutation in enumerate(mutator.explore(target_ast), start=1):
                print(f" - [#{index:>4}] {target_module.__name__} {site_mutation.operator_name:<3}: ", end="")
                with site_mutation():
                    try:
                        code = compile(target_ast, target_module.__name__, "exec")
                        mutant = types.ModuleType(target_module.__name__)
                        exec(code, mutant.__dict__)
                    except Exception as error:
                        print(error)
                        print(f"[{0:.5f}s] Incompetent")
                        score[INCOMPETENT] += 1
                    else:
                        with timer() as experiment:
                            result = test_runner.run(max_duration, mutant)
                        print(f"[{experiment.duration:.5f}s] {result.state} {result.killer}")
                        score[result.state] += 1

    # Report results.
    all_mutants = sum(score.values())
    bottom = score[SURVIVED] + score[KILLED] + score[TIMEOUT]
    percentage = ((score[KILLED] + score[TIMEOUT]) / bottom) if bottom else 0

    print(f"Mutation score [{total.duration:.5f}s]: {percentage:.1%}")
    print(f"  - All: {all_mutants}")

    if all_mutants:
        print(f"  - Killed: {score[KILLED]} ({score[KILLED] / all_mutants:.1%}%)")
        print(f"  - Survived: {score[SURVIVED]} ({score[SURVIVED] / all_mutants:.1%}%)")
        print(f"  - Incompetent: {score[INCOMPETENT]} ({score[INCOMPETENT] / all_mutants:.1%})")
        print(f"  - Timeout: {score[TIMEOUT]} ({score[TIMEOUT] / all_mutants:.1%})")
