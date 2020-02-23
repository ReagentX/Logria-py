"""
Unit Tests for sessions
"""

from os import remove
from pathlib import Path
import unittest
from logria.utilities import session
from logria.utilities.constants import SAVED_SESSIONS_PATH


class TestSessionHandler(unittest.TestCase):
    """
    Test cases to ensure constants are the expected values
    """

    def test_can_setup_handler(self):
        """
        Test that we can create an instance of the class
        """
        s = session.SessionHandler()
        self.assertIsInstance(s, session.SessionHandler)

    def test_setup_folder(self):
        """
        Ensure we correctly setup the folder in the expected place
        """
        s = session.SessionHandler()
        s.setup_folder()
        self.assertEqual(s.folder, Path(Path.home(), SAVED_SESSIONS_PATH))

    def test_sessions(self):
        """
        Test that we can get the sessions as a dict
        """
        s = session.SessionHandler()
        actual = s.sessions()
        expected = {0: '.DS_Store', 1: 'File - readme',
                    2: 'File - Sample Access Log', 3: 'Cmd - Generate Test Logs'}
        self.assertEqual(actual, expected)

    def test_show_sessions(self):
        """
        Test that we can get the sessions as a list
        """
        s = session.SessionHandler()
        actual = s.show_sessions()
        expected = ['0: .DS_Store',
                    '1: File - readme',
                    '2: File - Sample Access Log',
                    '3: Cmd - Generate Test Logs']
        self.assertEqual(actual, expected)

    def test_session_parsing(self):
        """
        Test that we properly show sessions from the directory as a list
        """
        s = session.SessionHandler()
        d = s.sessions()
        l = s.show_sessions()
        self.assertEqual([f'{i}: {d[i]}' for i in d], l)

    def test_load_session(self):
        """
        Test that both ways we load sessions are the same
        """
        s = session.SessionHandler()
        sessions = s.sessions()
        first_item = list(sessions.keys())[1]
        actual = s.load_session(first_item)
        expected = {'commands': [
            [
                'Users',
                'me',
                'Documents',
                'Code',
                'Python',
                'logria',
                'README.md'
            ]
        ],
            'type': 'file'
        }
        self.assertEqual(actual, expected)

    def test_save_session(self):
        """
        Test that we can write a session if we need to
        """
        s = session.SessionHandler()
        s.save_session('Test', ['ls', '-l'], 'cmd')
        remove(s.folder / 'Test')


class TestSessionBuilder(unittest.TestCase):
    """
    Tests the constructor methods of a SessionHander
    """

    def test_set_params(self):
        s = session.SessionHandler()
        command = ['ls', '-l']
        type_ = 'command'
        s.set_params(command, type_)
        self.assertEqual(s._commands, [command])
        self.assertEqual(s._type, type_)

    def test_as_list_command(self):
        s = session.SessionHandler()
        command = ['ls', '-l']
        command_2 = ['grep', '-nr', 'code', '.']
        type_ = 'command'
        s.set_params(command, type_)
        s.add_command(command_2)
        expected = ['Type:', '  command',
                    'Commands:', '  ls -l', '  grep -nr code .']
        self.assertEqual(s.as_list(), expected)

    def test_as_list_file(self):
        s = session.SessionHandler()
        command = ['usr', 'log', 'cloud-init.log']
        command_2 = ['usr', 'log', 'cloud-init-output.log']
        type_ = 'file'
        s.set_params(command, type_)
        s.add_command(command_2)
        expected = ['Type:', '  file', 'Files:',
                    '  usr/log/cloud-init.log', '  usr/log/cloud-init-output.log']
        self.assertEqual(s.as_list(), expected)
