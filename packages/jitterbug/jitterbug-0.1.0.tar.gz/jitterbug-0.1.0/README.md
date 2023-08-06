# Jitterbug

Jitterbug is a mutation testing tool for fuzzing parallel code.
It supports [py.test](https://docs.pytest.org/en/latest/) tests in Python 3.8+.

From article at Wikipedia:

> **Mutation testing** evaluates the quality of software tests.
> Mutation testing involves modifying a program's source code or byte code in small ways.
> A test suite that does not detect and reject the mutated code is considered defective.

## Quickstart

Jitterbug is available on [PyPI](https://pypi.org/project/jitterbug/), so it can be installed via:

    $ pip install jitterbug --user --upgrade

Run jitterbug specifying the location of your code and its unit tests:

    $ python -m jitterbug --source <PATH TO SOURCE> --test <PATH TO UNIT TESTS>
