from logria import app_name, version


def get_titlebar_text():
    """
    Creates the titlebar text
    """
    return [
        ("class:title", f" {app_name if version > 1 else 'Beta Name'}: {version} "),
        ("class:title", " (Press [Ctrl-Q] to quit.)"),
    ]
