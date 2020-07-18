"""
Logria command handler
"""
import curses


from logria.utilities import constants
# from logria.communication.shell_output import Logria


def handle_command(logria: 'Logria'):  # type: ignore
    """
    Enable command mode
    """
    # Handle smart poll rate
    if logria.smart_poll_rate:
        # Make it smooth to type
        logria.update_poll_rate(constants.SLOWEST_POLL_RATE)
    # Handle getting input from the command line for commands
    logria.activate_prompt(':')
    command = logria.box.gather().strip()
    curses.curs_set(0)
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
            logria.config_mode()
        elif ':history' in command:
            if command == ':history off':
                logria.reset_parser()
            else:
                try:
                    num_to_get = int(command.replace(':history', ''))
                except ValueError:
                    num_to_get = logria.height  # Default to screen height if no info given
                logria.start_history_mode(num_to_get)
    logria.reset_command_line()
    logria.write_to_command_line(logria.current_status)
