from contextlib import contextmanager
from time import perf_counter as time_provider
import ast


def notmutate(sth):
    return sth


@contextmanager
def timer():
    start = time_provider()
    t = type("", (), {})()
    yield t
    t.duration = time_provider() - start


def create_ast(code):
    root = ast.parse(code)
    # Add in parent mappings.
    root.parent = None
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return root


def is_docstring(node):
    def_node = node.parent.parent
    return (
        isinstance(def_node, (ast.FunctionDef, ast.ClassDef, ast.Module))
        and def_node.body
        and isinstance(def_node.body[0], ast.Expr)
        and isinstance(def_node.body[0].value, ast.Str)
        and def_node.body[0].value == node
    )
