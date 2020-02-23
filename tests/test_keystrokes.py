"""
Unit Tests for keystrokes
"""

import unittest
from logria.utilities import keystrokes


class TestValidator(unittest.TestCase):
    """
    Test cases to ensure keystrokes are set to expected values
    """

    def test_validator(self):
        """
        Test that we correctly validate keystrokes
        """
        for i in range(300):
            if i != 127:
                self.assertEqual(keystrokes.validator(i), i)
            else:
                self.assertEqual(keystrokes.validator(i), 263)
