"""
Class to handle parsing of standard log patterns
"""

import os
import re
import json
import pprint
from pathlib import Path

from logria.utilities.constants import ANSI_COLOR_PATTERN, SAVED_PATTERNS_PATH


class Parser():
    def __init__(self, pattern=None, type_=None, name=None, example=None):
        self._pattern = pattern  # The raw pattern
        # The type of pattern to parse, string {'split', 'regex'}
        self._type = type_
        self._name = name  # The name of the pattern
        self._example = example  # An example used to list on the frontend

    def get_name(self):
        return self._name

    def set_pattern(self, pattern: str, type_: str, name: str, example: str) -> None:
        self._pattern = pattern
        self._type = type_
        self._name = name
        self._example = example

    def clean_ansi_codes(self, string: str) -> str:
        return re.sub(ANSI_COLOR_PATTERN, '', string)

    def split_pattern(self, message: str) -> str:
        if self._pattern is None:
            raise ValueError('Parsing pattern when pattern not set!')
        parts = re.split(self._pattern, message)
        return parts

    def regex_pattern(self, message: str) -> str:
        if self._pattern is None:
            raise ValueError('Parsing pattern when pattern not set!')
        matches = re.match(self._pattern, message)
        return list(matches.groups())

    def parse(self, message: str) -> list:
        if self._type == 'split':
            return self.split_pattern(message)
        elif self._type == 'regex':
            return self.regex_pattern(message)
        else:
            raise ValueError(f'{self._type} is not a valid Parser type!')

    def as_dict(self):
        """
        Dict representation
        """
        return {'pattern': self._pattern,
                'type': self._type,
                'name': self._name,
                'example': self._example
                }

    def save(self) -> None:
        # Convert to json
        if self._pattern:
            d = self.as_dict()
            with open(Path(SAVED_PATTERNS_PATH, self._name), 'w') as f:
                f.write(json.dumps(d, indent=4))

    def load(self, name: str) -> None:
        # Convert to json
        if self._pattern is not None:
            raise ValueError('Setting pattern while pattern already set!')
        patterns = set(os.listdir(SAVED_PATTERNS_PATH))
        if name in patterns:
            with open(Path(SAVED_PATTERNS_PATH, name), 'r') as f:
                d = json.loads(f.read())
                self.set_pattern(d['pattern'], d['type'],
                                 d['name'], d['example'])

    def display_example(self):
        if self._pattern == None:
            raise ValueError('Display called without loading a parser!')
        match = self.parse(self._example)
        return [f'{i}: {v}' for i, v in enumerate(match)]

    @classmethod
    def patterns(cls) -> dict:
        patterns = os.listdir(SAVED_PATTERNS_PATH)
        return dict(zip(range(0, len(patterns)), patterns))

    @classmethod
    def show_patterns(cls) -> dict:
        patterns = os.listdir(SAVED_PATTERNS_PATH)
        return [f'{i}: {v}' for i, v in enumerate(patterns)]


if __name__ == '__main__':
    log_message = '2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message'
    log_message_short = '200 - simp - CRI - critical message'
    color_log_message = '\u001b[33m2020-02-04 19:06:52,852 \u001b[0m- \u001b[34m__main__.<module> \u001b[0m- \u001b[32mMainProcess \u001b[0m- \u001b[36mINFO \u001b[0m- I am a log! 91'
    std_log_message = '127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'

    def parse_std_log():
        p = Parser()
        # p.set_pattern(r'([^ ]*) ([^ ]*) ([^ ]*) \[([^]]*)\] "([^"]*)" ([^ ]*) ([^ ]*)', 'regex', 'Common Log Format', std_log_message)
        # p.set_pattern(r'- ', 'split', 'Color + Hyphen Separated', color_log_message)
        # p.set_pattern(r' - ', 'split', 'Hyphen Separated', log_message)
        p.load('Hyphen Separated')
        v = p.display_example()
        for i in v:
            print(i)
        # d = p.parse(log_message)
        # for i in d:
        #     print(f'{d.index(i)}:', i)
        # p.save()
    # parse_std_log()
    print(Parser().show_patterns())
