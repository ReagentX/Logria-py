"""
Logria editing bar commands
"""


# from logria.communication.shell_output import Logria


def toggle_insert_mode(logria: 'Logria'):  # type: ignore
    """
    Toggle insert mode
    """
    if logria.insert_mode:
        logria.insert_mode = False
    else:
        logria.insert_mode = True
    logria.build_command_line()
