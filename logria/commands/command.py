"""
Logria command handler
"""
import curses

from logria.commands.parser import reset_parser
from logria.utilities import constants
from logria.commands.config import config_mode

# from logria.communication.shell_output import Logria


def start_history_mode(logria: 'Logria', last_n: int) -> None:  # type: ignore
    """
    Swap message pointer to history tape
    """
    # Store previous message pointer
    if logria.messages is logria.stderr_messages:
        logria.previous_messages = logria.stderr_messages
    elif logria.messages is logria.stdout_messages:
        logria.previous_messages = logria.stdout_messages

    # Set new message pointer
    logria.messages = logria.box.history_tape.tail(last_n=last_n)


def handle_command(logria: 'Logria') -> None:  # type: ignore
    """
    Enable command mode
    """
    # Handle smart poll rate
    if logria.smart_poll_rate:
        # Make it smooth to type
        logria.update_poll_rate(constants.FASTEST_POLL_RATE)
    # Handle getting input from the command line for commands
    logria.activate_prompt(':')
    command = logria.box.gather().strip()
    curses.curs_set(0)
    # Since we parse info out of these strings we cannot use a dictionary to store
    #   the callable map like we do in the main app
    if command:
        if command == ':q':
            logria.stop()
        elif ':poll' in command:
            try:
                new_poll_rate = float(command.replace(':poll', ''))
            except ValueError:
                pass
            else:
                logria.update_poll_rate(new_poll_rate)
        elif ':config' in command:
            config_mode(logria)
        elif ':history' in command:
            if command == ':history off':
                reset_parser(logria)
            else:
                try:
                    num_to_get = int(command.replace(':history', ''))
                except ValueError:
                    num_to_get = logria.height  # Default to screen height if no info given
                start_history_mode(logria, num_to_get)
    logria.reset_command_line()
    logria.write_to_command_line(logria.current_status)
