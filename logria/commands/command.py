"""
Logria command handler
"""
import curses

from logria.commands.parser import reset_parser
from logria.utilities import constants
from logria.commands.config import config_mode
from logria.communication.setup import setup_streams

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
        elif command[:5] == ':poll':
            try:
                new_poll_rate = float(command.replace(':poll', ''))
            except ValueError:
                pass
            else:
                logria.update_poll_rate(new_poll_rate)
        elif command[:7] == ':config':
            config_mode(logria)
        elif command[:8] == ':history':
            if command == ':history off':
                reset_parser(logria)
            else:
                try:
                    num_to_get = int(command.replace(':history', ''))
                except ValueError:
                    num_to_get = logria.height  # Default to screen height if no info given
                start_history_mode(logria, num_to_get)
        elif command[:8] == ':restart':
            # Kill all streams
            for stream in logria.streams:
                stream.exit()
            # Remove them from Logria
            logria.streams = []
            # Reset messages buffers
            logria.stderr_messages = []
            logria.stdout_messages = []
            logria.parsed_messages = []
            logria.matched_rows = []
            # Setup new streams
            setup_streams(logria)
    logria.reset_command_line()
    logria.write_to_command_line(logria.current_status)
