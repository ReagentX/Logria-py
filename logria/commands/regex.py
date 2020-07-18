"""
Logria regex handler
"""


import curses

from logria.utilities import constants
from logria.utilities.regex_generator import regex_test_generator
from logria.logger.processor import process_matches

# from logria.communication.shell_output import Logria


def reset_regex_status(logria: 'Logria') -> None:  # type: ignore
    """
    Reset current regex/filter status to no filter
    """
    if logria.parser:
        logria.current_status = f'Parsing with {logria.parser.get_name()}, field {logria.parser_index}'
    else:
        logria.current_status = 'No filter applied'  # CLI message, rendered after
    logria.previous_render = None  # Reset previous render
    logria.func_handle = None  # Disable filter
    logria.highlight_match = False  # Disable highlighting
    logria.regex_pattern = ''  # Clear the current pattern
    logria.matched_rows = []  # Clear out matched rows
    logria.last_index_regexed = 0  # Reset the last searched index
    logria.current_end = 0  # We now do not know where to end
    logria.stick_to_bottom = True  # Stay at the bottom for the next render
    logria.write_to_command_line(logria.current_status)  # Render status


def handle_regex_command(logria: 'Logria', command: str) -> None:  # type: ignore
    """
    Handle a regex command
    """
    reset_regex_status(logria)
    logria.func_handle = regex_test_generator(command)
    logria.highlight_match = True
    logria.regex_pattern = command

    # Tell the user what is happening since this is synchronous
    logria.current_status = f'Searching buffer for regex /{logria.regex_pattern}/'
    logria.write_to_command_line(logria.current_status)

    # Process any new matched messages to render
    process_matches(logria)

    # Tell the user we are now filtering
    logria.current_status = f'Regex with pattern /{logria.regex_pattern}/'
    logria.write_to_command_line(logria.current_status)

    # Render the text
    logria.render_text_in_output()
    curses.curs_set(0)


def handle_regex(logria: 'Logria'):  # type: ignore
    """
    Handle when user activates regex mode, including parsing textbox message
    """
    # Handle smart poll rate
    if logria.smart_poll_rate:
        # Make it smooth to type
        logria.update_poll_rate(constants.SLOWEST_POLL_RATE)
    if not logria.analytics_enabled:  # Disable regex in analytics view
        # Handle getting input from the command line for regex
        logria.activate_prompt()
        command = logria.box.gather().strip()
        if command:
            if command == ':q':
                reset_regex_status(logria)
            else:
                handle_regex_command(logria, command)
        else:
            # If command is an empty string, ignore the input
            reset_regex_status(logria)
            logria.reset_command_line()


def toggle_highlight(logria: 'Logria'):  # type: ignore
    """
    Toggle highlighting of search matches
    """
    logria.previous_render = None  # Force render
    if logria.func_handle and logria.highlight_match:
        logria.highlight_match = False
    elif logria.func_handle and not logria.highlight_match:
        logria.highlight_match = True
    else:
        logria.highlight_match = False
