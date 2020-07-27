"""
Unit Tests for fs module
"""

import unittest
from pathlib import Path

from logria.utilities import fs


class TestListDirectory(unittest.TestCase):
    """
    Test cases to ensure InputStream can be initialized
    """

    def test_can_resolve_dir_str(self):
        """
        Test that we can resolve a string path
        """
        result = fs.listdir('/', {'.DS_Store'})
        self.assertIsInstance(result, list)

    def test_can_resolve_dir_path(self):
        """
        Test that we can resolve a Pathlib path
        """
        result = fs.listdir(Path('/'), {'.DS_Store'})
        self.assertIsInstance(result, list)

    def test_resolve_invalid_path(self):
        """
        Test that we don't crash if the path does not exist
        """
        result = fs.listdir(Path('a/b/c/d/e/f/g'), {'.DS_Store'})
        self.assertListEqual(result, [])

    def test_can_remove_pattern(self):
        """
        Test that pattern removal works
        """
        result = fs.listdir(Path('/'), {'dev'})
        if result is not None:
            self.assertNotIn('dev', result)
