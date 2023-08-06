# Jitterbug

Jitterbug is a testing tool for fuzzing parallel code.
It does this by randomly inserting ``sleep`` commands into various places in your code before each test run.
This is a great way to test the stability of multithreaded or parallel code.

Jitterbug supports [py.test](https://docs.pytest.org/en/latest/) tests in Python 3.8+.

## Quickstart

Jitterbug is available on [PyPI](https://pypi.org/project/jitterbug/), so it can be installed via:

    $ pip install jitterbug --user --upgrade

Run jitterbug specifying the location of your code and its unit tests:

    $ python -m jitterbug --source <PATH TO SOURCE> --test <PATH TO UNIT TESTS>
