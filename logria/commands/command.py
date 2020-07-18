"""
Logria command handler
"""


# from logria.communication.shell_output import Logria


def handle_command(logria: 'Logria'):
    """
    Enable command mode
    """
    logria.handle_command_mode()
