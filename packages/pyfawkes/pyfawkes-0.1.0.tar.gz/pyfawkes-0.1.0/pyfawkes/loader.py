from pathlib import Path

import inspect
import pkgutil
import sys
import os
import importlib

from importlib._bootstrap_external import EXTENSION_SUFFIXES, ExtensionFileLoader


def load(names, skip=None, exclude_c_extensions=True):
    skip = {} if skip is None else skip
    for name in names:
        for module in load_single(name):
            # yield only if module is not explicitly excluded and only source modules (.py) if demanded
            if module not in skip and not (exclude_c_extensions and _is_c_extension(module)):
                yield module

def load_single(name):
    full_path = os.path.abspath(name)
    if os.path.exists(full_path):
        if os.path.isfile(full_path):
            yield from load_file(full_path)
        elif os.path.isdir(full_path):
            yield from load_directory(full_path)
    elif is_package(name):
        yield from load_package(name)
    else:
        yield from load_module(name)

def load_file(name):
    if name.endswith(".py"):
        dirname = os.path.dirname(name)
        ensure_in_path(dirname)
        module_name = os.path.basename(os.path.splitext(name)[0])
        yield from load_module(module_name)

def load_package(name):
    try:
        package = importlib.import_module(name)
    except ImportError:
        return

    for _, module_name, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if ispkg:
            continue
        try:
            module = importlib.import_module(module_name)
            yield module
        except ImportError:
            pass

def load_directory(name):
    path = Path(name)
    if (path / "__init__.py").is_file():
        parent_dir = path.parent
        ensure_in_path(parent_dir)
        yield from load_package(path.name)
        return

    for subpath in path.glob("*"):
        if subpath.is_file():
            yield from load_file(subpath)
        else:  # subpath is directory:
            yield from load_directory(subpath)

def load_module(name):
    module_path = name.split(".")
    for i in reversed(range(len(module_path) + 1)):
        try:
            module = importlib.import_module(".".join(module_path[:i]))
            member_path = module_path[i:]
            if _module_has_member(module, member_path):
                yield module
                return
            else:
                raise RuntimeError(f"cant load {name}")
        except ImportError:
            pass

# Utilities.

def ensure_in_path(directory):
    if directory not in sys.path:
        sys.path.insert(0, directory)

def is_package(name):
    try:
        module = importlib.import_module(name)
        return hasattr(module, "__file__") and module.__file__.endswith("__init__.py")
    except ImportError:
        return False
    finally:
        sys.path_importer_cache.clear()

def _module_has_member(module, member_path):  # Count: 1
    for part in member_path:
        if not hasattr(module, part):
            return False
        module = getattr(module, part)
    return True

def _is_c_extension(module):
    if isinstance(getattr(module, "__loader__", None), ExtensionFileLoader):
        return True
    module_filename = inspect.getfile(module)
    module_filetype = os.path.splitext(module_filename)[1]
    return module_filetype in EXTENSION_SUFFIXES
