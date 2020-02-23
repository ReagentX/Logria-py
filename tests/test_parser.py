"""
Unit Tests for parser
"""

import unittest
from os import remove
from collections import Counter
from pathlib import Path

from logria.logger import parser
from logria.utilities.constants import SAVED_PATTERNS_PATH


class TestPatternSetup(unittest.TestCase):
    """
    Test cases to ensure parser are the expected values
    """

    def test_can_setup_parser(self):
        """
        Ensure we can setup the parser
        """
        p = parser.Parser()
        self.assertIsInstance(p, parser.Parser)

    def test_setup_folder(self):
        """
        Ensure we correctly setup the folder in the expected place
        """
        p = parser.Parser()
        p.setup_folder()
        self.assertEqual(p.folder, Path(Path.home(), SAVED_PATTERNS_PATH))

    def test_get_name(self):
        """
        Test that we correctly get the current filter name
        """
        sample_name = 'test'
        p = parser.Parser(name=sample_name)
        self.assertEqual(p.get_name(), sample_name)

    def test_set_pattern(self):
        """
        Test that we successfully init the data in the parser
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 34'
        p.set_pattern(' - ', 'split', 'Hyphen Separated', log_message, {})
        self.assertEqual(p._pattern, r' - ')
        self.assertEqual(p._type, 'split')
        self.assertEqual(p.get_name(), 'Hyphen Separated')
        self.assertEqual(p._example, log_message)
        self.assertEqual(p._analytics_methods, {})


class TestPatternAnalytics(unittest.TestCase):
    """
    Test cases to ensure we can handle analytics properly
    """

    def test_handle_analytics_for_message(self):
        """
        Test that we can handle analytics, this is a wrapper for `apply_analytics`
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        p.handle_analytics_for_message(log_message)
        p.handle_analytics_for_message(log_message)
        expected = {0: None, 1: Counter(
            {'simple_example': 2}), 2: Counter({'CRITICAL': 2}), 3: 0}
        self.assertEqual(p.analytics, expected)

    def test_reset_analytics(self):
        """
        Test that we can reset analytics after capturing some
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        p.handle_analytics_for_message(log_message)
        p.handle_analytics_for_message(log_message)
        p.reset_analytics()
        expected = {}
        self.assertEqual(p.analytics, expected)

    def test_get_analytics_for_index(self):
        """
        Test that we correctly handle extracting analytics
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        for index, name in enumerate(analytics_methods.keys()):
            self.assertEqual(p.get_analytics_for_index(index), name)

    def test_analytics_to_list(self):
        """
        Test that we can get the analytics data as a list
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        p.handle_analytics_for_message(log_message)
        p.handle_analytics_for_message(log_message)
        expected = ['Caller', '  simple_example: 2', 'Level',
                    '  CRITICAL: 2', 'Message', '  Total: 44']
        self.assertEqual(p.analytics_to_list(), expected)


class TestStringParserMethods(unittest.TestCase):
    """
    Test that we correctly parse strings
    """

    def test_extract_numbers_from_message_int(self):
        """
        Test that we properly parse ints from strings
        """
        p = parser.Parser()
        message = 'abc123a'
        actual = p.extract_numbers_from_message(message)
        self.assertEqual(actual, 123)
        self.assertIsInstance(actual, int)

    def test_extract_numbers_from_message_float(self):
        """
        Test that we properly parse floats from strings
        """
        p = parser.Parser()
        message = 'abc12.3a'
        actual = p.extract_numbers_from_message(message)
        self.assertEqual(actual, 12.3)
        self.assertIsInstance(actual, float)

    def test_clean_ansi_codes(self):
        """
        Test that we successfully remove escape codes from a log
        """
        p = parser.Parser()
        log_message = '\u001b[33m2005-03-19 15:10:26,773 \u001b[0m- \u001b[33msimple_example \u001b[0m- \u001b[33mCRITICAL \u001b[0m- \u001b[33mcritical message 22'
        expected = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        self.assertEqual(p.clean_ansi_codes(log_message), expected)

    def test_split_pattern(self):
        """
        Test that we can split a message as we expect
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        actual = p.split_pattern(log_message)
        expected = [
            '2005-03-19 15:10:26,773',
            'simple_example',
            'CRITICAL',
            'critical message 22'
        ]
        self.assertEqual(actual, expected)

    def test_regex_pattern(self):
        """
        Test that we can regex a message as we expect
        """
        p = parser.Parser()
        log_message = '127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326'
        p.set_pattern("([^ ]*) ([^ ]*) ([^ ]*) \\[([^]]*)\\] \"([^\"]*)\" ([^ ]*) ([^ ]*)", 'regex', 'Common Log Format',
                      log_message, {})
        actual = p.regex_pattern(log_message)
        expected = [
            '127.0.0.1',
            'user-identifier',
            'frank',
            '10/Oct/2000:13:55:36 -0700',
            'GET /apache_pb.gif HTTP/1.0',
            '200',
            '2326'
        ]
        self.assertEqual(actual, expected)

    def test_parse_message_split(self):
        """
        Test that we can split a message through the abstraction
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        actual = p.parse(log_message)
        expected = [
            '2005-03-19 15:10:26,773',
            'simple_example',
            'CRITICAL',
            'critical message 22'
        ]
        self.assertEqual(actual, expected)

    def test_parse_message_regex(self):
        """
        Test that we can regex a message through the abstraction
        """
        p = parser.Parser()
        log_message = '127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326'
        p.set_pattern("([^ ]*) ([^ ]*) ([^ ]*) \\[([^]]*)\\] \"([^\"]*)\" ([^ ]*) ([^ ]*)", 'regex', 'Common Log Format',
                      log_message, {})
        actual = p.parse(log_message)
        expected = [
            '127.0.0.1',
            'user-identifier',
            'frank',
            '10/Oct/2000:13:55:36 -0700',
            'GET /apache_pb.gif HTTP/1.0',
            '200',
            '2326'
        ]
        self.assertEqual(actual, expected)


class TestPatternInteraction(unittest.TestCase):
    """
    Tests for methods that interact with parser properties
    """

    def test_as_dict(self):
        """
        Test that the dictionary representation is accurate
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        actual = p.as_dict()
        expected = {
            'pattern': ' - ',
            'type': 'split',
            'name': 'Hyphen Separated',
            'example': '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22',
            'analytics': {
                'Date': 'date',
                'Caller': 'count',
                'Level': 'count',
                'Message': 'sum'
            }
        }
        self.assertEqual(actual, expected)

    def test_as_list(self):
        """
        Test that the dictionary representation is accurate
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        actual = p.as_list()
        expected = [
            'Pattern:  - ',
            'Type: split',
            'Name: Hyphen Separated',
            'Example: 2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22',
            "Analytics: {'Date': 'date', 'Caller': 'count', 'Level': 'count', 'Message': 'sum'}"]
        self.assertEqual(actual, expected)

    def test_save_load(self):
        """
        Test that we can successfully save and load items
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        name = 'Test Run'
        p.set_pattern(' - ', 'split', name,
                      log_message, analytics_methods)
        saved = p.as_dict()
        p.save()
        p2 = parser.Parser()
        p2.load(name)
        loaded = p2.as_dict()
        self.assertEqual(loaded, saved)
        remove(Path(p2.folder) / name)

    def test_display_example(self):
        """
        Test that we properly format the example parsed message
        """
        p = parser.Parser()
        log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message 22'
        analytics_methods = {
            "Date": "date",
            "Caller": "count",
            "Level": "count",
            "Message": "sum"
        }
        p.set_pattern(' - ', 'split', 'Hyphen Separated',
                      log_message, analytics_methods)
        actual = p.display_example()
        expected = [
            '0: 2005-03-19 15:10:26,773',
            '1: simple_example',
            '2: CRITICAL',
            '3: critical message 22'
        ]
        self.assertEqual(actual, expected)

    def test_patterns(self):
        """
        Test that we read patterns as dict
        """
        p = parser.Parser()
        self.assertIsInstance(p.patterns(), dict)

    def test_show_patterns(self):
        """
        Test that we read patterns as list
        """
        p = parser.Parser()
        self.assertIsInstance(p.show_patterns(), list)
