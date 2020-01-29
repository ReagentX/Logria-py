from logria import app_name


def get_titlebar_text():
    """
    Creates the titlebar text
    """
    return [
        ("class:title", f" {app_name} "),
        ("class:title", " (Press [Ctrl-Q] to quit.)"),
    ]
