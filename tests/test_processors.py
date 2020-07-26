"""
Unit Tests for processors
"""

import os
import unittest

from logria.communication.shell_output import Logria
from logria.logger.processor import process_matches, process_parser
from logria.logger.parser import Parser
from logria.utilities import regex_generator


class TestProcessors(unittest.TestCase):
    """
    Test cases to ensure keystrokes are set to expected values
    """

    def test_process_matches(self):
        """
        Test that we correctly process matches
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(20)]

        # Set regex function, process
        app.func_handle = regex_generator.regex_test_generator(r'\d')
        process_matches(app)

        self.assertEqual(app.messages, [str(x) for x in range(20)])

    def test_process_parser_no_analytics(self):
        """
        Test that we correctly process parsers
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(10)]
        app.parser_index = 0
        app.last_index_processed = 0

        # Set parser, activate
        app.parser = Parser(
            pattern=r'(\d)',
            type_='regex',
            name='Test',
            example='4',
            analytics_methods={
                'Item': 'average'
            }
        )

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(app.messages, [str(x) for x in range(10)])

    def test_process_parser_analytics_average(self):
        """
        Test that we correctly process parsers
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(10)]
        app.parser_index = 0
        app.last_index_processed = 0
        app.analytics_enabled = True

        # Set parser, activate
        app.parser = Parser(
            pattern=r'(\d)',
            type_='regex',
            name='Test',
            example='4',
            analytics_methods={
                'Item': 'average'
            }
        )

        # Set analytics method manually
        app.parser._analytics_map = dict(
            zip(range(len(app.parser._analytics_methods.keys())), app.parser._analytics_methods.keys()))

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(app.messages, [
                         'Item', '  average:\t 4.50', '  count:\t 10.00', '  total:\t 45.00'])

    def test_process_parser_analytics_count(self):
        """
        Test that we correctly process parsers
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(10)]
        app.parser_index = 0
        app.last_index_processed = 0
        app.analytics_enabled = True

        # Set parser, activate
        app.parser = Parser(
            pattern=r'(\d)',
            type_='regex',
            name='Test',
            example='4',
            analytics_methods={
                'Item': 'count'
            }
        )

        # Set analytics method manually
        app.parser._analytics_map = dict(
            zip(range(len(app.parser._analytics_methods.keys())), app.parser._analytics_methods.keys()))

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(
            app.messages, ['Item', '  0: 1', '  1: 1', '  2: 1', '  3: 1', '  4: 1'])

    def test_process_parser_analytics_sum(self):
        """
        Test that we correctly process parsers
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(10)]
        app.parser_index = 0
        app.last_index_processed = 0
        app.analytics_enabled = True

        # Set parser, activate
        app.parser = Parser(
            pattern=r'(\d)',
            type_='regex',
            name='Test',
            example='4',
            analytics_methods={
                'Item': 'sum'
            }
        )

        # Set analytics method manually
        app.parser._analytics_map = dict(
            zip(range(len(app.parser._analytics_methods.keys())), app.parser._analytics_methods.keys()))

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(app.messages, ['Item', '  Total: 45'])
