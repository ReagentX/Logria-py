"""
Simple script to generate test logs
"""

import random
import time
from logria.logger.default_logger import setup_default_logger

# Setup default logger
LOGGER = setup_default_logger(__name__)


LOGGER.info('I am the first log in the list! %s', 0)
while True:
    LOGGER.info('I am a log! %s', random.randint(1, 100))
    print('I am standard output', flush=True)
    time.sleep(0.01)
