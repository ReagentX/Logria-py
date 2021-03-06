"""
Tests the app launcher
"""

import os
import unittest
from curses import error

from logria.communication.input_handler import (CommandInputStream,
                                                FileInputStream)
from logria.communication.shell_output import Logria


class TestCanLaunchApp(unittest.TestCase):
    """
    Tests various ways we can launch the app
    """

    def test_launch_no_stream(self):
        """
        Test that we can launch the app
        This should crash only due to a curses error
        """
        with self.assertRaises(error):
            os.environ['TERM'] = 'dumb'
            app = Logria(None, False)
            app.start()

    def test_launch_with_command_stream(self):
        """
        Test that we can launch the app
        This should crash only due to a curses error
        """
        with self.assertRaises(error):
            os.environ['TERM'] = 'dumb'
            stream = CommandInputStream(['ls', '-l'])
            app = Logria(stream, False)
            app.start()

    def test_launch_with_file_stream(self):
        """
        Test that we can launch the app
        This should crash only due to a curses error
        """
        with self.assertRaises(error):
            os.environ['TERM'] = 'dumb'
            stream = FileInputStream(['readme.md'])
            app = Logria(stream, False)
            app.start()
