"""
Sample Log parsing class to deliver some statistics
"""


import ast
import re
import statistics
import time
from collections import Counter

from logria.logger.log_parser import Log
from logria.logger.default_logger import setup_default_logger

# Setup default logger
LOGGER = setup_default_logger(__name__)


class ParseStandardLog():
    """
    Class to scaffold some basic statistics
    """

    def __init__(self):
        self.types_dict = Counter()
        self.providers = Counter()
        self.callers = Counter()
        self.errors = Counter()
        self.cached_requests = Counter()
        self.mean = {'total': 0, 'count': 0, 'value': 0}


    def handle_number(self, message: str) -> str:
        number = int(re.sub("\D", "", message))
        self.mean['total'] += number
        self.mean['count'] += 1
        self.mean['value'] = self.mean['total'] / self.mean['count']


    def print_results(self) -> None:
        """
        Handles printing the results of the log file symbolication
        """
        print('Message Types:')
        for log_type, frequency in self.types_dict.most_common():
            print(f'\t{log_type}: {frequency:,}')
        print('Providers:')
        for provider, frequency in self.providers.most_common():
            print(f'\t{provider}: {frequency:,}')
        print('Callers:')
        for caller, frequency in self.callers.most_common():
            print(f'\t{caller}: {frequency:,}')
        print('Errors:')
        for error, frequency in self.errors.most_common():
            print(f'\t{error}: {frequency:,}')
        print('Cached queries:')
        for cache_type, count in self.cached_requests.most_common():
            print(f'\t{cache_type}: {count}')
        print(self.mean['value'])


        # if self.values:
        #     print('Render Statistics (s)')
        #     print(f'\tMaximum:\t{max(self.values, default="None")}')
        #     print(f'\tMinimum:\t{min(self.values, default="None")}')
        #     print(f'\tAverage:\t{statistics.mean(self.values):0.2f}')
        #     print(f'\tMedian: \t{statistics.median(self.values):0.2f}')
        #     print(f'\tStdev:  \t{statistics.stdev(self.values):0.2f}')


    def handle(self, log):
        """
        To download logs to test:

        scp -i dev-dna.pem ec2-user@10.191.37.231:.pm2/logs/Chargemaster-Engine-error.log .pm2/logs
        """
        t_0 = time.perf_counter()

        log = Log(log.replace('\n', ''))  # Clean up line end
        if log.is_valid_log:
            self.types_dict.update([log.type])
            self.callers.update([log.caller])
            if log.type == 'ERROR':
                self.errors.update([log.message])
            # Handle messages
            elif 'I am a log!' in log.message:
                self.handle_number(log.message)

        # End performance counter
        t_1 = time.perf_counter() - t_0
        # LOGGER.debug(f'Processed log file in: {t_1:0.4f}s')
        self.print_results()
