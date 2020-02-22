"""
Unit Tests for regex_generator
"""

import unittest
from logria.utilities import regex_generator


class TestRegexGenerator(unittest.TestCase):
    """
    Test cases to ensure regex_generator is handling data properly
    """

    def test_validator(self):
        """
        Test that we correctly generate a pattern
        """
        self.assertTrue(callable(regex_generator.regex_test_generator('-')))

    def test_generated_regex_func(self):
        """
        Test that we properly generate a regex function
        """
        pattern = regex_generator.regex_test_generator('-')
        self.assertTrue(pattern('-'))

    def test_generated_regex_func_with_color_code(self):
        """
        Test that we match properly against a string with escape codes
        """
        pattern = regex_generator.regex_test_generator(' - ')
        self.assertTrue(pattern(' \u001b[0m-\u001b[32m '))


class TestRealLength(unittest.TestCase):
    """
    Test that we properly get real lengths
    """

    def test_get_real_length(self):
        """
        Test that we get the real length of a string
        """
        self.assertEqual(regex_generator.get_real_length('word'), 4)

    def test_get_real_length_with_color_code(self):
        """
        Test that we get the real length of a string with escape codes
        """
        self.assertEqual(regex_generator.get_real_length(
            '\u001b[0m word \u001b[32m'), 6)
