import sys
from pathlib import Path

import dynamic_imports
import pytest
from dynamic_imports import importers

from test_pkg import functions


def test_import_module_from_file_path():
    module_path = Path(__file__).parent.joinpath("test_pkg/functions.py")
    module = importers.import_module(module_path)
    assert module.__name__.split(".")[-1] == functions.__name__.split(".")[-1]


def test_load_module_from_name():
    module = importers.import_module("dynamic_imports")
    assert module.__name__.split(".")[-1] == dynamic_imports.__name__.split(".")[-1]


def test_import_module_attr():
    module_path = Path(__file__).parent.joinpath("test_pkg/functions.py")
    function = importers.import_module_attr(module_path, "sleep_return_1")
    assert function.__name__ == "sleep_return_1"


def test_import_module_attr_error():
    module_path = Path(__file__).parent.joinpath("test_pkg/functions.py")
    with pytest.raises(AttributeError):
        importers.import_module_attr(module_path, "sleep_return_2")
