"""
Contains utilities and constants that control how the app handles regex
"""

import re
from typing import Callable

from logria.utilities.constants import ANSI_COLOR_PATTERN


def regex_test_generator(pattern: str) -> Callable:
    """
    Return a function that will test a string against `pattern`
    Ignores characters in ANSI color escape codes
    """
    return lambda string: bool(re.search(pattern,
                                         re.sub(ANSI_COLOR_PATTERN,
                                                '',
                                                string)))


def get_real_length(item: str) -> int:
    """
    Get the real length of a string without escape codes
    """
    return len(re.sub(ANSI_COLOR_PATTERN, '', item))
