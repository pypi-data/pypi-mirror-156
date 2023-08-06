from collections import defaultdict
from contextlib import contextmanager
from glob import glob
from importlib import import_module
from os.path import dirname, basename, isfile, join
import ast
import inspect
import re

from pyfawkes.operators import all_mixins
from pyfawkes.utils import notmutate

METHOD_PATTERN = re.compile(rf"mutate_([A-Za-z0-9]+)($|(_\w+)+$)")


class SiteMutation:
    def __init__(self, operator_name, node, new_node):
        self.operator_name = operator_name
        self.node = node
        self.new_node = new_node
        self.parent = self.node.parent
        for field, value in ast.iter_fields(self.parent):
            if isinstance(value, list):
                for index, child in enumerate(value):
                    if isinstance(child, ast.AST) and child == node:
                        self.parent_field = field
                        self.parent_index = index
                        self.parent_field_original = list(value)
            elif isinstance(value, ast.AST) and value == node:
                self.parent_field = field
                self.parent_index = None
                self.parent_field_original = value

    @contextmanager
    def __call__(self):
        if self.parent_index is None:
            if self.new_node is None:
                delattr(self.parent, self.parent_field)
            else:
                setattr(self.parent, self.parent_field, self.new_node)
            yield
            setattr(self.parent, self.parent_field, self.parent_field_original)
        else:
            if self.new_node is None:
                del getattr(self.parent, self.parent_field)[self.parent_index]
            else:
                getattr(self.parent, self.parent_field)[self.parent_index] = self.new_node
            yield
            setattr(self.parent, self.parent_field, self.parent_field_original)

    def __contains__(self, other):
        return any(node == other.node for node in ast.walk(self.node))


def add_abbreviations(cls):
    cls.all_methods = []
    for attr in dir(cls):
        if match := METHOD_PATTERN.match(attr):
            method = getattr(cls, attr)
            superclass_name = method.__qualname__.split(".")[0]
            method.abbr = "".join(letter for letter in superclass_name if letter.isupper())
            method.name = " ".join(word.lower() for word in re.findall("[A-Z][a-z]*", superclass_name))
            method.node = match.group(1)
            cls.all_methods.append(method.abbr)
    return cls


@add_abbreviations
class Mutator(*all_mixins):
    def __init__(self, operator_abbreviations):
        self.transformers = defaultdict(list)
        for attr in dir(self):
            method = getattr(self, attr)
            if hasattr(method, "abbr") and method.abbr in operator_abbreviations:
                self.transformers[method.node].append(method)

    def explore(self, root):
        for node in ast.walk(root):
            for transformer in self.transformers[node.__class__.__name__]:
                for new_node in transformer(node):
                    ast.fix_missing_locations(new_node)
                    yield SiteMutation(transformer.abbr, node, new_node)

    def has_notmutate(self, node):  # Unused.
        try:
            return any(decorator.id == notmutate.__name__ for decorator in node.decorator_list)
        except AttributeError:
            return False
