import random
import time
import sys
import logging

logger = logging.Logger(__name__, level='INFO')
while True:
    logger.warning(f'I am a log! {random.randint(1, 100)}')
    time.sleep(0.5)
