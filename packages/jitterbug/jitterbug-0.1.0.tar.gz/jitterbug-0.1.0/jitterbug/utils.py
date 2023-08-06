from contextlib import contextmanager
from time import perf_counter as time_provider
import ast


def notmutate(func):
    return func


@contextmanager
def timer():
    start = time_provider()
    t = type("", (), {})()
    yield t
    t.duration = time_provider() - start


def create_ast(code):
    root = ast.parse(code)
    for node in ast.walk(root):
        if hasattr(node, "decorator_list") and any(decorator.id == notmutate.__name__ for decorator in node.decorator_list):
            node.not_mutate = True

        if hasattr(node, "not_mutate"):
            for child in ast.iter_child_nodes(node):
                child.not_mutate = True

    return root
