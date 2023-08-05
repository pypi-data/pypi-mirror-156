import os
import sys

from inspect import getmembers, isfunction
from importlib import import_module
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import Callable
from urllib.parse import urlparse

from .constants import ENTRYPOINT_ATTR, PIPELINE_ENV_VAR
from .models import PipelineSource


def in_container() -> bool:
    return bool(os.environ.get(PIPELINE_ENV_VAR))


def is_entrypoint(func: Callable) -> bool:
    return hasattr(func, ENTRYPOINT_ATTR)


def is_remote_location(location: str) -> bool:
    try:
        result = urlparse(location)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def nbconvert(notebook: bytes) -> bytes:
    command = [
        "jupyter-nbconvert",
        "--stdin",
        "--stdout",
        "--to=python",
        "--TagRemovePreprocessor.enabled=True",
        "--TagRemovePreprocessor.remove_cell_tags=pachyderm-ignore"
    ]
    result = run(command, capture_output=True, input=notebook)
    return result.stdout


def script_to_module(location: os.PathLike) -> PipelineSource:

    location = Path(location)
    original = source = location.read_bytes()
    if location.suffix == ".ipynb":
        source = nbconvert(original)

    module_name = "__pipeline_script"
    with TemporaryDirectory() as tempdir:
        test_script = Path(tempdir, f"{module_name}.py")
        test_script.write_bytes(source)

        sys.path.append(tempdir)
        try:
            try:
                sys.stdout, sys.stderr = os.devnull, os.devnull
                module = import_module(module_name)
            finally:
                sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
            del sys.modules[module_name]
        except ImportError as err:
            raise RuntimeError(
                "Could not import the script. "
                "The script must be entirely self contained. "
                "Are all your dependencies installed? "
            ) from err
        assert sys.path.pop() == tempdir

    pipeline_source = PipelineSource(module, location, original, source)
    return pipeline_source


def get_entrypoint(module: ModuleType) -> Callable:
    """Returns the only function within the specified module marked with the
    @pipeline decorator.

    Args:
        module: The module to search.

    Raises:
        RuntimeError: If none or multiple entrypoints are found.

    Returns:
        Entrypoint function to the pipeline.
    """
    entrypoints = [
        func for _name, func in getmembers(module, isfunction)
        if is_entrypoint(func)
    ]
    if not entrypoints:
        raise RuntimeError(
            "No entrypoints found. "
            "Did you mark a function with the @pipeline decorator?"
        )
    if len(entrypoints) > 1:
        raise RuntimeError(
            "Multiple entrypoints found. "
            "Please only mark a single function with the @pipeline decorator."
        )
    return entrypoints[0]
