"""
Filesystem interaction functions
"""


import os
from pathlib import Path
from typing import Union


def listdir(path: Union[str, Path], ignored_patterns: set):
    """
    os.listdir wrapper that ignores patterns
    """
    return [x for x in os.listdir(path) if x not in ignored_patterns]
