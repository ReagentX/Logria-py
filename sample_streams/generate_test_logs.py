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
    RANDINT = random.randint(1, 100)
    if RANDINT % 5 == 0:
        LOGGER.warning('I am a first log! %s', RANDINT)
    LOGGER.info('I am a first log! %s', RANDINT)
    # String formatting is too slow
    print('I am standard output %s' % RANDINT, flush=True)
    time.sleep(0.1)
