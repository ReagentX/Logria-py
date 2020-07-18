"""
Commands for scrolling the window
"""


# from logria.communication.shell_output import Logria
from logria.utilities import constants

def up(logria: 'Logria'):  # type: ignore
    """
    Scroll one line up
    """
    # Smooth scroll
    logria.update_poll_rate(constants.FASTEST_POLL_RATE)
    # Scroll up
    logria.manually_controlled_line = True
    logria.stick_to_top = False
    logria.stick_to_bottom = False
    logria.current_end = max(0, logria.current_end - 1)
    logria.previous_render = None  # Force render


def down(logria: 'Logria'):  # type: ignore
    """
    Scroll one line down
    """
    # Smooth scroll
    logria.update_poll_rate(constants.FASTEST_POLL_RATE)
    # Scroll down
    logria.manually_controlled_line = True
    logria.stick_to_top = False
    logria.stick_to_bottom = False
    if logria.matched_rows:
        logria.current_end = min(
            len(logria.matched_rows) - 1, logria.current_end + 1)
    else:
        logria.current_end = min(
            len(logria.messages) - 1, logria.current_end + 1)
    logria.previous_render = None  # Force render


def bottom(logria: 'Logria'):  # type: ignore
    """
    Stick to bottom
    """
    logria.stick_to_top = False
    logria.stick_to_bottom = True
    logria.manually_controlled_line = False


def top(logria: 'Logria'):  # type: ignore
    """
    Stick to top
    """
    logria.stick_to_top = True
    logria.stick_to_bottom = False
    logria.manually_controlled_line = False