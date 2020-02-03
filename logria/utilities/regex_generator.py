"""
Contains utilities and constants that control how the app handles regex
"""

import re


ANSI_COLOR_PATTERN = r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]'


def regex_test_generator(pattern: str) -> callable:
    """
    Return a function that will test a string against `pattern`
    Ignores charachers in ANSI color escape codes
    """
    return lambda string: bool(re.search(pattern,
                                         re.sub(ANSI_COLOR_PATTERN,
                                                '',
                                                string)))
