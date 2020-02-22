"""
Unit Tests for input_handler
"""

import unittest
from logria.communication import input_handler


class TestInputStream(unittest.TestCase):
    """
    Test cases to ensure InputStream can be initialized
    """

    def test_create_input_stream(self):
        """
        Test that we can crate an InputStream
        """
        i = input_handler.InputStream(['ls', '-l'])
        self.assertIsInstance(i, input_handler.InputStream)

    def test_cannot_start_process(self):
        """
        Test that parent InputStream cannot start processes
        Unit tests cannot be pickled, so this test case will never work
        """
        # i = input_handler.InputStream(['ls', '-l'])
        # with self.assertRaises(NotImplementedError):
        #     i.start()
        pass

    def test_can_exit(self):
        """
        Test that parent InputStream can exit processes
        Unit tests cannot be pickled, so this test case will never work
        """
        i = input_handler.InputStream(['ls', '-l'])
        with self.assertRaises(AttributeError):
            i.exit()


class TestCommandInputStream(unittest.TestCase):
    """
    Test cases to ensure CommandInputStream can be initialized
    """

    def test_create_command_input_stream(self):
        """
        Test that we can create a CommandInputStream
        """
        i = input_handler.CommandInputStream(['ls', '-l'])
        self.assertIsInstance(i, input_handler.CommandInputStream)


class TestFileInputStream(unittest.TestCase):
    """
    Test cases to ensure FileInputStream can be initialized
    """

    def test_create_file_input_stream(self):
        """
        Test that we can create a FileInputStream
        """
        i = input_handler.FileInputStream(['ls', '-l'])
        self.assertIsInstance(i, input_handler.FileInputStream)


class TestPipeInputStream(unittest.TestCase):
    """
    Test cases to ensure PipeInputStream can be initialized
    """

    def test_create_pipe_input_stream(self):
        """
        Test that we can create a PipeInputStream
        """
        i = input_handler.PipeInputStream(['ls', '-l'])
        self.assertIsInstance(i, input_handler.PipeInputStream)
