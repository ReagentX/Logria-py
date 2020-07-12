"""
Unit Tests for constants
"""

import unittest
from logria.utilities import constants


class TestFormattingFunctions(unittest.TestCase):
    """
    Test cases to ensure constants are the expected values
    """

    def test_ansi_color_pattern(self):
        """
        Ensure ANSI_COLOR_PATTERN is the expected value
        """
        self.assertEqual(constants.ANSI_COLOR_PATTERN,
                         r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

    def test_root_folder(self):
        """
        Ensure LOGRIA_ROOT is the expected value
        """
        self.assertEqual(constants.LOGRIA_ROOT, '.logria')

    def test_saved_patterns_path(self):
        """
        Ensure SAVED_PATTERNS_PATH is the expected value
        """
        self.assertEqual(constants.SAVED_PATTERNS_PATH, f'{constants.USER_HOME}/.logria/patterns')

    def test_saved_sessions_path(self):
        """
        Ensure SAVED_SESSIONS_PATH is the expected value
        """
        self.assertEqual(constants.SAVED_SESSIONS_PATH, f'{constants.USER_HOME}/.logria/sessions')
