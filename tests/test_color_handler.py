"""
Unit Tests for color handler
"""


import unittest

from logria.interface import color_handler


class TestColorHandler(unittest.TestCase):
    """
    Test cases to ensure InputStream can be initialized
    """

    def test_sanitize_null(self):
        """
        Test that we remove null bytes from a string
        """
        sample = '\x00test\x00'
        self.assertEqual(color_handler._sanitize(sample), 'test')

    def test_sanitize_no_null(self):
        """
        Test that we just return the clean string
        """
        sample = 'test'
        self.assertEqual(color_handler._sanitize(sample), 'test')

    def test_sanitize_no_color(self):
        """
        Test that we do not remove color bytes from a string
        """
        sample = '\033test\033'
        self.assertEqual(color_handler._sanitize(sample), '\033test\033')
