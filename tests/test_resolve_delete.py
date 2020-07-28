"""
Unit Tests for setup functions
"""

import unittest

from logria.commands.config import resolve_delete_command


class SetupValidator(unittest.TestCase):
    """
    Test cases to ensure setup operates correctly
    """

    def test_resolve_single_num(self):
        """
        Test that we correctly validate 1 singleton
        """
        resolved = resolve_delete_command(':r 1')
        self.assertCountEqual(resolved, [1])

    def test_resolve_double_num(self):
        """
        Test that we correctly a 2 singletons
        """
        resolved = resolve_delete_command(':r 1,2')
        self.assertCountEqual(resolved, [1, 2])

    def test_resolve_triple_num(self):
        """
        Test that we correctly validate 3 singletons
        """
        resolved = resolve_delete_command(':r 1,2,3')
        self.assertCountEqual(resolved, [1, 2, 3])

    def test_resolve_triple_num_trailing_comma(self):
        """
        Test that we correctly validate 3 singletons with trailing comma
        """
        resolved = resolve_delete_command(':r 1,2,3,')
        self.assertCountEqual(resolved, [1, 2, 3])

    def test_resolve_range(self):
        """
        Test that we correctly validate 1 range
        """
        resolved = resolve_delete_command(':r 1-5')
        self.assertCountEqual(resolved, [1, 2, 3, 4, 5])

    def test_resolve_double_range(self):
        """
        Test that we correctly validate two ranges
        """
        resolved = resolve_delete_command(':r 1-3,5-7')
        self.assertCountEqual(resolved, [1, 2, 3, 5, 6, 7])

    def test_resolve_triple_range(self):
        """
        Test that we correctly validate three ranges
        """
        resolved = resolve_delete_command(':r 1-3,5-7,9-11')
        self.assertCountEqual(resolved, [1, 2, 3, 5, 6, 7, 9, 10, 11])

    def test_resolve_ranges_with_singletons(self):
        """
        Test that we correctly validate ranges with singletons
        """
        resolved = resolve_delete_command(':r 1-3,5,9-11,15')
        self.assertCountEqual(resolved, [1, 2, 3, 5, 9, 10, 11, 15])

    def test_resolve_ranges_multiple_dash(self):
        """
        Test that we correctly validate range with multiple dashes
        """
        resolved = resolve_delete_command(':r 1--3,4')
        self.assertCountEqual(resolved, [4])

    def test_resolve_ranges_with_string(self):
        """
        Test that we correctly delete with range
        """
        resolved = resolve_delete_command(':r a-b,4')
        self.assertCountEqual(resolved, [4])
