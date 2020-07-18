"""
Logria window content display handler
"""


from logria.commands.regex import reset_regex_status
# from logria.communication.shell_output import Logria


def swap_input(logria: 'Logria'):  # type: ignore
    """
    Swap between stderr and stdout
    """
    logria.previous_render = None  # Force render
    # Swap stdout and stderr
    logria.reset_parser()
    reset_regex_status(logria)
    if logria.messages is logria.stderr_messages:
        logria.messages = logria.stdout_messages
    else:
        logria.messages = logria.stderr_messages


def resize(logria: 'Logria'):  # type: ignore
    """
    Resize window
    """
    logria.handle_resize()
