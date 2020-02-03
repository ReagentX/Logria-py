def validator(key):
    # Handle backspace on MacOS
    if key == 127:
        return 263  # Ctrl-h
    return key
