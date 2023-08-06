# PyFawkes

PyFawkes is a mutation testing too.
It supports [py.test](https://docs.pytest.org/en/latest/) tests in Python 3.5+.

From article at Wikipedia:

> **Mutation testing** evaluates the quality of software tests.
> Mutation testing involves modifying a program's source code or byte code in small ways.
> A test suite that does not detect and reject the mutated code is considered defective.

## Quickstart

PyFawkes is available on [PyPI](https://pypi.org/project/pyfawkes/), so it can be installed via:

    $ pip install pyfawkes --user --upgrade

Run PyFawkes specifying the location of your code and its unit tests:

    $ python -m pyfawkes --source <PATH TO SOURCE> --test <PATH TO UNIT TESTS>
