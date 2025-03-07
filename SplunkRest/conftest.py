# configure include paths that are needed for execution of doctest unit tests of the project
import os
import sys

_app_path = os.path.abspath(os.path.dirname(__file__))
_bin_path = os.path.join(_app_path, "bin")
_lib_path = os.path.join(_app_path, "lib")
if _bin_path not in sys.path:
    sys.path.insert(0, _bin_path)
if _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

import pytest


@pytest.fixture(scope="session")
def app_path():
    return _app_path


@pytest.fixture(scope="session")
def app():
    return os.path.basename(_app_path)
