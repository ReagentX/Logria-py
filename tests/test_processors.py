"""
Unit Tests for processors
"""

import os
import unittest

from logria.communication.shell_output import Logria
from logria.logger.parser import Parser
from logria.logger.processor import process_matches, process_parser
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
        Test that we correctly process parser with no analytics
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
        app.parser = Parser()
        app.parser.set_pattern(
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

    def test_process_parser_invalid_index(self):
        """
        Test that we correctly process parser with invalid index
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
        app.messages = [f'{x}+{x}+{x}' for x in range(10)]
        app.parser_index = 3
        app.last_index_processed = 0

        # Set parser, activate
        app.parser = Parser()
        app.parser.set_pattern(
            pattern='\+',
            type_='split',
            name='Test',
            example='a-a',
            analytics_methods={
                'Item 1': 'count',
                'Item 2': 'count'
            }
        )

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(app.messages, [])

    def test_process_parser_analytics_average(self):
        """
        Test that we correctly process parser with average metric
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
        app.parser = Parser()
        app.parser.set_pattern(
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
        Test that we correctly process parser with count metric
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
        app.parser = Parser()
        app.parser.set_pattern(
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
        Test that we correctly process parsers with sum metric
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
        app.parser = Parser()
        app.parser.set_pattern(
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

    def test_process_parser_analytics_invalid(self):
        """
        Test that we correctly process parser with invalid metric
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
        app.parser = Parser()
        app.parser.set_pattern(
            pattern=r'(\d)',
            type_='fake_type',
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
        with self.assertRaises(ValueError):
            process_parser(app)

    def test_process_parser_analytics_too_many_matches(self):
        """
        Test that we correctly process parser with too many matches
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
        app.messages = [str(x) for x in range(10, 20)]
        app.parser_index = 0
        app.last_index_processed = 0
        app.analytics_enabled = True

        # Set parser, activate
        app.parser = Parser()
        app.parser.set_pattern(
            pattern=r'(\d)(\d)',
            type_='regex',
            name='Test',
            example='4',
            analytics_methods={
                'Item': 'invalid'
            }
        )

        # Set analytics method manually
        app.parser._analytics_map = dict(
            zip(range(len(app.parser._analytics_methods.keys())), app.parser._analytics_methods.keys()))

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(app.messages, [])

    def test_process_parser_regex_no_pattern(self):
        """
        Test that we correctly process regex parser with no pattern
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
        app.parser = Parser()
        app.parser.set_pattern(
            pattern=None,
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
        with self.assertRaises(ValueError):
            process_parser(app)

    def test_process_parser_regex(self):
        """
        Test that we correctly process regex parser
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
        app.parser = Parser()
        app.parser.set_pattern(
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
        self.assertEqual(app.messages, [str(x) for x in range(10)])

    def test_process_parser_split_no_pattern(self):
        """
        Test that we correctly process parser with split no pattern
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
        app.parser = Parser()
        app.parser.set_pattern(
            pattern=None,
            type_='split',
            name='Test',
            example='4',
            analytics_methods={
                'Item': 'average'
            }
        )

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        with self.assertRaises(ValueError):
            process_parser(app)

    def test_process_parser_analytics_split(self):
        """
        Test that we correctly process split parsers
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
        app.messages = [f'{x}|{x // 2}' for x in range(10)]
        app.parser_index = 1
        app.last_index_processed = 0

        # Set parser, activate
        app.parser = Parser()
        app.parser.set_pattern(
            pattern=r'\|',
            type_='split',
            name='Test',
            example='4|4',
            analytics_methods={
                'Item 1': 'count',
                'Item 2': 'sum'
            }
        )

        # Store previous message pointer
        app.previous_messages = app.messages

        # Process parser
        process_parser(app)

        self.assertEqual(app.messages, [f'{x // 2}' for x in range(10)])

    def test_process_parser_analytics_average_no_numbers(self):
        """
        Test that we correctly process a parser with average metric but no source numbers
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
        app.messages = [chr(x) for x in range(64, 80)]
        app.parser_index = 0
        app.last_index_processed = 0
        app.analytics_enabled = True

        # Set parser, activate
        app.parser = Parser()
        app.parser.set_pattern(
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

        # Since we manually construct alaytics, create the the key
        app.parser.analytics[0] = None
        self.assertIsNone(app.parser.apply_analytics(0, 'A'))
