"""
Class to handle parsing of standard log patterns
"""

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import List, Union

from logria.utilities.constants import ANSI_COLOR_PATTERN, SAVED_PATTERNS_PATH


class Parser():
    """
    Handles setting up of log message parsing
    """

    def __init__(self, pattern=None, type_=None, name=None, example=None, analytics_methods=None, num_to_print=5):
        self._pattern: str = pattern  # The raw pattern
        # The type of pattern to parse, string {'split', 'regex'}
        self._type: str = type_
        self._name: str = name  # The name of the pattern
        self._example: str = example  # An example used to list on the frontend
        # Analytics methods to use when parsing
        self._analytics_methods: dict = analytics_methods
        # Stores the map of the message index to the analytics method names
        self.num_to_print = num_to_print  # Number of items to print in analytics output
        self._analytics_map: dict = {}
        self.analytics: dict = {}  # Analytics the main script can access
        self.setup_folder()

    def setup_folder(self):
        """
        Set workspace folder, create if nonexistent
        """
        if Path(SAVED_PATTERNS_PATH).exists():
            pass
        else:
            os.mkdir(Path(SAVED_PATTERNS_PATH))
        self.folder = Path(SAVED_PATTERNS_PATH)

    def get_name(self):
        """
        Get the name of the parser as a string
        """
        return self._name

    def set_pattern(self, pattern: str, type_: str, name: str, example: str, analytics_methods: dict) -> None:
        """
        Init the class variables when loading
        """
        self._pattern = pattern
        self._type = type_
        self._name = name
        self._example = example
        self._analytics_methods = analytics_methods
        self._analytics_map = dict(
            zip(range(len(analytics_methods.keys())), analytics_methods.keys()))

    def reset_analytics(self) -> None:
        """
        Resets the current analytics dictionary
        """
        self.analytics = {}

    def get_analytics_for_index(self, index: int) -> str:
        """
        Returns the name of the item that is the provided index
        """
        return self._analytics_map[index]

    # pylint: disable=no-self-use
    def extract_numbers_from_message(self, message: str) -> Union[int, float]:
        r"""
        We do not use regex replacement here because...

        % python -m timeit '"".join(c for c in "sdkjh987978asd098as0980a98sd" if c.isdigit() or c == ".")'
        100000 loops, best of 3: 3.47 usec per loop
        % python -m timeit 'import re; re.sub(r"[^\d\.]", "", "sdkjh987978asd098as0980a98sd")'
        100000 loops, best of 3: 4.67 usec per loop
        """
        digits = "".join(c for c in message if c.isdigit() or c == ".")
        out_num = float(digits)
        if out_num.is_integer():
            return int(out_num)
        return out_num

    def apply_analytics(self, index: int, part: str) -> None:
        """
        Applies an analytics rule to a message
        """
        # Figure out what rule we want to apply
        rule_name = self.get_analytics_for_index(index)
        rule = self._analytics_methods[rule_name]
        if rule == 'count':
            if not self.analytics[index]:
                self.analytics[index] = Counter()
            self.analytics[index].update([part])
        elif rule == 'sum':
            if not self.analytics[index]:
                self.analytics[index] = 0
            try:
                val = self.extract_numbers_from_message(part)
                self.analytics[index] += val
            except ValueError:
                pass
        elif rule == 'average':
            if not self.analytics[index]:
                self.analytics[index] = {'average': 0, 'count': 0, 'total': 0}
            try:
                val = self.extract_numbers_from_message(part)
                self.analytics[index]['count'] += 1
                self.analytics[index]['total'] += val
                self.analytics[index]['average'] = self.analytics[index]['total'] / \
                    self.analytics[index]['count']
            except ValueError:
                pass

    def handle_analytics_for_message(self, message: str) -> None:
        """
        Applies the analytics rules for each part of a message
        """
        if message:
            parsed_message = self.parse(message)
            if parsed_message is not None:
                for index, part in enumerate(parsed_message):
                    if index not in self.analytics:
                        self.analytics[index] = None
                    try:
                        self.apply_analytics(index, part)
                    except KeyError:
                        # If we matched too many fields, this message is invalid
                        pass

    def analytics_to_list(self) -> List[str]:
        """
        Return the existing parsed analytics as a list
        """
        out_l = []
        for stat in self.analytics:
            value = self.analytics[stat]
            if value is None:
                continue
            out_l += [f'{self.get_analytics_for_index(stat)}']
            if isinstance(value, Counter):
                out_l += [f'  {item}: {count:,}' for item,
                          count in value.most_common(self.num_to_print)]
            elif isinstance(value, (int, float)):
                out_l += [f'  Total: {value:,}']
            elif isinstance(value, dict):
                out_l += [f'  {key}:\t {value[key]:,.2f}' for key in value]
        return out_l

    def clean_ansi_codes(self, string: str) -> str:
        """
        Remove ANSI escape sequences from a string
        """
        return re.sub(ANSI_COLOR_PATTERN, '', string)

    def split_pattern(self, message: str) -> List[str]:
        """
        Split a log message based on a delimiter
        """
        if self._pattern is None:
            raise ValueError('Parsing pattern when pattern not set!')
        parts = re.split(self._pattern, message)
        return parts

    def regex_pattern(self, message: str) -> List[str]:
        """
        Split a log message based on matches to a regex pattern
        """
        if self._pattern is None:
            raise ValueError('Parsing pattern when pattern not set!')
        matches = re.match(self._pattern, message)
        return list(matches.groups()) if matches is not None else []

    def parse(self, message: str) -> List[str]:
        """
        Parse a log message
        """
        if self._type == 'split':
            return self.split_pattern(message)
        elif self._type == 'regex':
            return self.regex_pattern(message)
        raise ValueError(f'{self._type} is not a valid Parser type!')

    def as_dict(self):
        """
        Dict representation
        """
        return {'pattern': self._pattern,
                'type': self._type,
                'name': self._name,
                'example': self._example,
                'analytics': self._analytics_methods
                }

    def as_list(self):
        """
        List representation
        """
        return [
            f'Pattern: {self._pattern}',
            f'Type: {self._type}',
            f'Name: {self._name}',
            f'Example: {self._example}',
            f'Analytics: {self._analytics_methods}'
        ]

    def save(self) -> None:
        """
        Save current pattern
        """
        # Convert to json
        if self._pattern:
            d = self.as_dict()
            with open(self.folder / self._name, 'w') as f:
                f.write(json.dumps(d, indent=4))

    def load(self, name: str) -> None:
        """
        Load existing pattern
        """
        # Convert to json
        if self._pattern is not None:
            raise ValueError('Setting pattern while pattern already set!')
        patterns = set(os.listdir(self.folder))
        if name in patterns:
            with open(self.folder / name, 'r') as f:
                d = json.loads(f.read())
                self.set_pattern(d['pattern'], d['type'],
                                 d['name'], d['example'], d['analytics'])
                self._analytics_map = dict(
                    zip(range(len(d['analytics'].keys())), d['analytics'].keys()))

    def display_example(self):
        """
        Show parser result so the user can choose what section to look at
        """
        if self._pattern is None:
            raise ValueError('Display called without loading a parser!')
        match = self.parse(self._example)
        return [f'{i}: {v}' for i, v in enumerate(match)]

    def patterns(self) -> dict:
        """
        Get the existing patterns as a dict
        """
        patterns = os.listdir(self.folder)
        return dict(zip(range(0, len(patterns)), patterns))

    def show_patterns(self) -> List[str]:
        """
        Get the existing patterns as a list
        """
        patterns = os.listdir(self.folder)
        return [f'{i}: {v}' for i, v in enumerate(patterns)]
