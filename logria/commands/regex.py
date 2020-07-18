"""
Logria regex handler
"""


# from logria.communication.shell_output import Logria


def handle_regex(logria: 'Logria'):  # type: ignore
    """
    Enable regex mode
    """
    logria.handle_regex_mode()


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
