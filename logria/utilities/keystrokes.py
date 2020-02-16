"""
Utilities to handle input validation
"""


def validator(key):
    """
    Intercept invalid strokes and convert them to valid ones
    """
    # Handle backspace on MacOS
    if key == 127:
        return 263  # Ctrl-h
    return key
