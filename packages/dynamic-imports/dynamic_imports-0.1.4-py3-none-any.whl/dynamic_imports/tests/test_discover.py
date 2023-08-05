from collections import Counter

from dynamic_imports import discover

import test_pkg
from test_pkg import l1_2
from test_pkg.base import Base


def test_non_recursive_module_name_discovery():
    module_names = discover.get_module_names(l1_2, search_subpackages=False)
    assert module_names == {"test_pkg.l1_2.m1", "test_pkg.l1_2.m2"}


def test_non_recursive_module_discovery():
    modules = discover.get_modules(l1_2, search_subpackages=False)
    module_names = {m.__name__ for m in modules}
    assert module_names == {"test_pkg.l1_2.m1", "test_pkg.l1_2.m2"}


def test_recursive_module_name_discovery():
    modules = discover.get_module_names(test_pkg, search_subpackages=True)
    module_names = {m.__name__ for m in modules}
    assert module_names == {
        "test_pkg.l1_1.m1",
        "test_pkg.l1_1.m2",
        "test_pkg.l1_2.l2_1.m1",
        "test_pkg.base",
        "test_pkg.functions",
        "test_pkg.l1_2.l2_1.m2",
        "test_pkg.l1_2.m1",
        "test_pkg.l1_2.m2",
    }

def test_recursive_module_discovery():
    modules = discover.get_modules(test_pkg, search_subpackages=True)
    module_names = {m.__name__ for m in modules}
    assert module_names == {
        "test_pkg.l1_1.m1",
        "test_pkg.l1_1.m2",
        "test_pkg.l1_2.l2_1.m1",
        "test_pkg.base",
        "test_pkg.functions",
        "test_pkg.l1_2.l2_1.m2",
        "test_pkg.l1_2.m1",
        "test_pkg.l1_2.m2",
    }


"""
def test_non_recursive_package_class_discovery():
    classes = discover.get_package_classes(
        l1_2, Base, recursive=False, import_classes=False
    )
    class_name_counts = Counter(classes)
    assert set(class_name_counts.keys()) == {"C1", "C2", "C3"}
    assert all(c == 1 for c in class_name_counts.values())


def test_recursive_package_class_discovery():
    classes = discover.get_package_classes(
        test_pkg, Base, recursive=True, import_classes=False
    )
    class_name_counts = Counter(classes)
    assert set(class_name_counts.keys()) == {"C1", "C2", "C3"}
    assert all(c == 3 for c in class_name_counts.values())
"""
# TODO test package class/name defs

def test_module_class_instances():
    