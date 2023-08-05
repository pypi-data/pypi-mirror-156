import importlib
import pkgutil
import pyclbr
from pathlib import Path
from types import ModuleType
from typing import List, Union

from .importers import import_module


def get_module_names(
    package: Union[ModuleType, str], search_subpackages: bool = True
) -> List[str]:
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
    return [
        name
        for _, name, ispkg in searcher(package.__path__, f"{package.__name__}.")
        if not ispkg
    ]


def get_modules(
    package: Union[ModuleType, str], search_subpackages: bool = True
) -> Union[List[str], List[ModuleType]]:
    """Find all modules in a package or nested packages.

    Args:
        package (ModuleType): Top-level package where search should be started.
        search_subpackages (bool, optional): Recurse into sub-packages. Defaults to True.

    Returns:
        List[str]: The discovered modules.
    """
    return [
        import_module(name) for name in get_module_names(package, search_subpackages)
    ]


def get_module_class_defs(
    base_class: Union[ModuleType, str], module: Union[ModuleType, str]
) -> List[ModuleType]:
    if isinstance(module, str):
        module = import_module(module)
    if isinstance(base_class, str):
        return [
            o
            for o in module.__dict__.values()
            if base_class in [c.__name__ for c in getattr(o, "__bases__", [])]
        ]
    return [
        o for o in module.__dict__.values() if base_class in getattr(o, "__bases__", [])
    ]


def get_module_class_def_names(
    base_class: Union[ModuleType, str], module: Union[ModuleType, str]
):
    base_class = base_class if isinstance(base_class, str) else base_class.__name__
    if isinstance(module, str):
        # check if module_name is path to a file.
        if (module_path := Path(module)).is_file():
            # read python file path
            module_classes = pyclbr.readmodule(
                module_path.stem, path=module_path.parent
            )
        else:
            # read installed module path.
            module_classes = pyclbr.readmodule(module)
        return [
            cls_name
            for cls_name, cls_obj in module_classes.items()
            if any(s.name == base_class for s in cls_obj.super)
        ]
    # parse the already imported module.
    return [c.__name__ for c in get_module_class_defs(base_class, module)]


def get_package_class_def_names(
    base_class: Union[ModuleType, str],
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
):
    """Find names of implementations of `base_class` in a module or package.

    Args:
        base_class (Union[ModuleType, str]): Base class who's derived implementations should be searched for.
        module_name (str): Name of module to search in.
        search_subpackages (bool, optional): Recurse into sub-packages. Defaults to True.
    Returns:
        List[ModuleType]: Imported classes.
    """
    class_def_names = []
    for module_name in get_module_names(package, search_subpackages):
        class_def_names += get_module_class_def_names(base_class, module_name)
    return class_def_names


def get_package_class_defs(
    base_class: Union[ModuleType, str],
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
):
    """Find all implementations of `base_class` in `module`.

    Args:
        class_type (Union[ModuleType, str]): Base class who's derived implementations should be searched for.
        module (ModuleType): Module to search in.


    Returns:
        Union[List[str], List[ModuleType]]: Imported classes or class names.
    """
    class_defs = []
    for module in get_modules(package, search_subpackages):
        class_defs += get_module_class_defs(base_class, module)
    return class_defs


def get_module_class_instances(module: Union[ModuleType, str], class_type: ModuleType):
    if isinstance(module, str):
        module = import_module(module)
    return [o for o in module.__dict__.values() if isinstance(o, class_type)]


def get_package_class_instances(
    class_type: ModuleType,
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
) -> List[ModuleType]:
    return [
        o
        for module in get_modules(package, search_subpackages)
        for o in module.__dict__.values()
        if isinstance(o, class_type)
    ]
