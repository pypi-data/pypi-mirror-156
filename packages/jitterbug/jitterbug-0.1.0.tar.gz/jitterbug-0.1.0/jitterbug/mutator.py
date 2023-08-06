from contextlib import contextmanager
from random import random
import ast

NODE_TYPES = [ast.FunctionDef]  # For, While, If, With, Try, ExceptHandler
DELAY_BODY = ast.parse('from time import sleep; sleep(0.01)').body

def mutate(root, n=10, prob=0.5):
    nodes = [node for node in ast.walk(root) if any(isinstance(node, node_type) for node_type in NODE_TYPES) and not hasattr(node, "not_mutate")]
    for _ in range(n):
        yield SiteMutation([node for node in nodes if random() <= prob])

class SiteMutation:
    def __init__(self, nodes):
        self.nodes = nodes
        self.original_bodies = {node: node.body for node in self.nodes}

    @contextmanager
    def __call__(self):
        for node in self.nodes:
            node.body = DELAY_BODY + list(node.body)
            ast.fix_missing_locations(node)
        yield
        for node, body in self.original_bodies.items():
            node.body = body
            ast.fix_missing_locations(node)
