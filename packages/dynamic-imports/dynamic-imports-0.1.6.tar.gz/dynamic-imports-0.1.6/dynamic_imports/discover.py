import importlib
import pkgutil
import pyclbr
from pathlib import Path
from types import ModuleType
from typing import Any, List, Union

from .importers import import_module


def get_modules(
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
    names_only: bool = False,
) -> Union[List[str], List[ModuleType]]:
    """Find names of all modules in a package or nested packages.

    Args:
        package (ModuleType): Top-level package where search should be started.
        search_subpackages (bool, optional): Search sub-packages. Defaults to True.

    Returns:
        List[str]: The discovered module names.
    """
    if isinstance(package, str):
        # argument is a package that has not been imported.
        package = importlib.import_module(package)
    # search package.
    searcher = pkgutil.walk_packages if search_subpackages else pkgutil.iter_modules
    module_names = [
        name
        for _, name, ispkg in searcher(package.__path__, f"{package.__name__}.")
        if not ispkg
    ]
    if names_only:
        return module_names
    return [import_module(name) for name in module_names]


def class_impl_from_module(
    base_class: Union[ModuleType, str],
    module: Union[ModuleType, str],
    names_only: bool = False,
) -> Union[List[str], List[ModuleType]]:
    if isinstance(module, str):
        if names_only:
            # check if module_name is path to a file.
            if (module_path := Path(module)).is_file():
                # read python file path
                module_classes = pyclbr.readmodule(
                    module_path.stem, path=module_path.parent
                )
            else:
                # read installed module path.
                module_classes = pyclbr.readmodule(module)
            base_class = (
                base_class if isinstance(base_class, str) else base_class.__name__
            )
            return [
                cls_name
                for cls_name, cls_obj in module_classes.items()
                if any(s.name == base_class for s in cls_obj.super)
            ]
        module = import_module(module)
    # parse the imported module.
    if isinstance(base_class, str):
        class_defs = [
            o
            for o in module.__dict__.values()
            if base_class in [c.__name__ for c in getattr(o, "__bases__", [])]
        ]
    else:
        class_defs = [
            o
            for o in module.__dict__.values()
            if base_class in getattr(o, "__bases__", [])
        ]
    if names_only:
        return [c.__name__ for c in class_defs]
    return class_defs


def class_impl_from_package(
    base_class: Union[ModuleType, str],
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
    names_only: bool = False,
) -> Union[List[str], List[ModuleType]]:
    """Find names of implementations of `base_class` in a module or package.

    Args:
        base_class (Union[ModuleType, str]): Base class who's derived implementations should be searched for.
        module_name (str): Name of module to search in.
        search_subpackages (bool, optional): Recurse into sub-packages. Defaults to True.
    Returns:
        List[ModuleType]: Imported classes.
    """
    class_impls = []
    for module in get_modules(package, search_subpackages, names_only):
        class_impls += class_impl_from_module(base_class, module, names_only)
    return class_impls


def class_instances_from_module(
    module: Union[ModuleType, str], class_type: ModuleType
) -> List[Any]:
    if isinstance(module, str):
        module = import_module(module)
    return [o for o in module.__dict__.values() if isinstance(o, class_type)]


def class_instances_from_package(
    class_type: ModuleType,
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
) -> List[Any]:
    return [
        o
        for module in get_modules(package, search_subpackages)
        for o in module.__dict__.values()
        if isinstance(o, class_type)
    ]
