"""
Unit Tests for color handler
"""


import unittest

from logria.interface import color_handler


class TestColorHandlerSatnitize(unittest.TestCase):
    """
    Test cases to ensure Color Handler will properly handle invalid characters
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


class TestColorHandlerCodes(unittest.TestCase):
    """
    Test that the Color Handler properly resolves color codes
    """

    def test_can_handle_real_color(self):
        """
        Test that we can parse valid colors
        """
        colors = [
            '[30m30[0m'
            '[31m31[0m'
            '[32m32[0m'
            '[33m33[0m'
            '[34m34[0m'
            '[35m35[0m'
            '[36m36[0m'
            '[40m40[0m'
            '[41m41[0m'
            '[42m42[0m'
            '[43m43[0m'
            '[44m44[0m'
            '[45m45[0m'
            '[46m46[0m'
            '[47m47[0m'
            '[90m90[0m'
            '[91m91[0m'
            '[92m92[0m'
            '[93m93[0m'
            '[94m94[0m'
            '[95m95[0m'
            '[96m96[0m'
            '[100m100[0m'
            '[101m101[0m'
            '[102m102[0m'
            '[103m103[0m'
            '[104m104[0m'
            '[105m105[0m'
            '[106m106[0m'
            '[107m107[0m'
        ]
        for color in colors:
            self.assertNotEqual(color_handler._color_str_to_color_pair(color), -1)

    def test_does_not_crash_invalid_color(self):
        """
        Test that we dont crash when given an invalid color
        """
        self.assertEqual(color_handler._color_str_to_color_pair('[108m108[0m'), 101)
