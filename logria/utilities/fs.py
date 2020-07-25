"""
Filesystem interaction functions
"""


import os
from pathlib import Path
from typing import Union, List


def listdir(path: Union[str, Path], ignored_patterns: set) -> List:
    """
    Safe os.listdir wrapper that ignores patterns in filenames
    """
    if os.path.exists(path) and os.path.isdir(path):
        return [x for x in os.listdir(path) if x not in ignored_patterns]
    return []
