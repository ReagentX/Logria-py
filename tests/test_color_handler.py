"""
Unit Tests for color handler
"""


import unittest

from logria.interface import color_handler


class TestColorHandler(unittest.TestCase):
    """
    Test cases to ensure InputStream can be initialized
    """

    def test_sanitize(self):
        sample = '\x00test\x00'
        self.assertEqual(color_handler._sanitize(sample), 'test')
