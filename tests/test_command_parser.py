"""
Unit Tests for command parser
"""

import os
import unittest
from pathlib import Path

from logria.utilities import command_parser


class TestFormattingFunctions(unittest.TestCase):
    """
    Test cases to ensure command parser are the expected values
    """

    def test_can_create_resolver(self):
        """
        Test that we can create a resolver instance
        """
        r = command_parser.Resolver()
        self.assertIsInstance(r, command_parser.Resolver)

    def test_can_get_user_home(self):
        """
        Test that we get the user's home folder properly
        """
        r = command_parser.Resolver()
        self.assertEqual(r.user_home, str(Path.home()))

    def test_can_resolve_real_path(self):
        """
        Test that we correctly resolve a real path
        """
        r = command_parser.Resolver()
        self.assertEqual(r.get('tail'), '/usr/bin/tail')

    def test_can_resolve_fake_path(self):
        """
        Test that we correctly resolve a fake path
        """
        r = command_parser.Resolver()
        self.assertEqual(r.get('tail123'), 'tail123')

    def test_resolve_home_dir(self):
        """
        Test that we resolve the proper strings to the user's home directory
        """
        r = command_parser.Resolver()
        expected = str(Path.home())
        self.assertEqual(r.resolve_home_dir('~'), expected)
        self.assertEqual(r.resolve_home_dir('$HOME'), expected)

    def test_resolve_command_as_string(self):
        """
        Test that we properly resolve a command to a string
        """
        r = command_parser.Resolver()
        actual = r.resolve_command_as_string(
            'tail -f $HOME/file.txt | cat -ne')
        expected = f'/usr/bin/tail -f {Path.home()}/file.txt | /bin/cat -ne'
        self.assertEqual(actual, expected)

    def test_resolve_command_as_list(self):
        """
        Test that we properly resolve a command to a list
        """
        r = command_parser.Resolver()
        actual = r.resolve_command_as_list(
            'tail -f ~/file.txt | cat -ne')
        expected = [
            '/usr/bin/tail',
            '-f',
            f'{Path.home()}/file.txt',
            '|',
            '/bin/cat',
            '-ne'
        ]
        self.assertEqual(actual, expected)

    def test_resolve_file_as_string(self):
        """
        Test that we properly resolve a file to a string
        """
        r = command_parser.Resolver()
        actual = r.resolve_file_as_str('$HOME/file.txt')
        expected = f'{Path.home()}/file.txt'
        self.assertEqual(actual, expected)

    def test_resolve_file_as_list(self):
        """
        Test that we properly resolve a file to a list
        """
        r = command_parser.Resolver()
        actual = r.resolve_file_as_list(
            '~/file.txt')
        expected = [
            f'{Path.home()}',
            'file.txt'
        ]
        self.assertEqual(actual, expected)


class TestParserPathEnv(unittest.TestCase):
    """
    Tests whether we correctly resolve PATH variables
    """
    def test_no_path(self):
        """
        Test we do not crash if the path varibale is missing
        """
        path_string = os.environ.pop("PATH")
        r = command_parser.Resolver()
        self.assertFalse(r._paths)
        # Put the PATH back for other tests
        os.environ["PATH"] = path_string

    def test_path_folder_missing(self):
        """
        Test we do not crash if the folder does not exist
        """
        os.environ['PATH'] += ':/a/a/b/b/c/c/d/d'
        r = command_parser.Resolver()
        self.assertTrue(r._paths)

    def test_file_on_path(self):
        """
        Test we do not crash if there is a file on the path, make sure it gets added
        """
        os.environ['PATH'] += ':~/.logria/sessions/.DS_Store'
        r = command_parser.Resolver()
        self.assertIn('.DS_Store', r._paths)
