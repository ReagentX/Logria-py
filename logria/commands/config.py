"""
Logria configuration handler
"""


from os.path import isfile

from logria.commands.parser import Parser
from logria.utilities import constants
from logria.utilities.command_parser import Resolver
from logria.utilities.session import SessionHandler

# from logria.communication.shell_output import Logria


def handle_create_session_file(logria: 'Logria', session: SessionHandler) -> bool:  # type: ignore
    """
    Handle manual session file creation
    """
    cmd_resolver = Resolver()  # The resolver we use to add commands

    logria.messages.append(constants.SESSION_ADD_FILE)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    session.set_type('file')
    logria.activate_prompt()
    file_path = logria.box.gather().strip()
    resolved_file_path = cmd_resolver.resolve_file_as_list(file_path)
    if isfile('/'.join(resolved_file_path)):
        session.add_command(resolved_file_path)
        logria.messages = session.as_list()
        logria.messages.append(constants.SESSION_SHOULD_CONTINUE_FILE)
        logria.previous_render = None  # Force render
        logria.render_text_in_output()
        logria.activate_prompt()
        user_done = logria.box.gather().strip()
        if user_done == ':s':
            logria.messages = [constants.SAVE_CURRENT_SESSION]
            logria.previous_render = None  # Force render
            logria.render_text_in_output()
            logria.activate_prompt()
            filename = logria.box.gather().strip()
            if filename == ':q':
                logria.stop()
            session.save_current_session(filename)
            return True
        elif user_done == ':q':
            logria.stop()
    elif file_path == ':q':
        logria.stop()
    else:
        logria.messages.append(f'Cannot resolve path: {"/".join(file_path)}')
        logria.previous_render = None  # Force render
        logria.render_text_in_output()
    return False


def handle_create_session_command(logria: 'Logria', session: SessionHandler) -> bool:  # type: ignore
    """
    Get user input to create a session
    """
    cmd_resolver = Resolver()  # The resolver we use to add commands
    logria.messages.append(constants.SESSION_ADD_COMMAND)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    session.set_type('command')
    logria.activate_prompt()
    command = logria.box.gather().strip()
    if command == ':q':
        logria.stop()
        return False
    resolved_command = cmd_resolver.resolve_command_as_list(command)
    session.add_command(resolved_command)
    logria.messages = session.as_list()
    logria.messages.append(constants.SESSION_SHOULD_CONTINUE_COMMAND)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    logria.activate_prompt()
    user_done = logria.box.gather().strip()
    if user_done == ':s':
        logria.messages = [constants.SAVE_CURRENT_SESSION]
        logria.previous_render = None  # Force render
        logria.render_text_in_output()
        logria.activate_prompt()
        filename = logria.box.gather().strip()
        session.save_current_session(filename)
        return True
    elif user_done == ':q':
        logria.stop()
    return False


def handle_create_session(logria: 'Logria') -> None:  # type: ignore
    """
    Handle the creation of new sessions
    """
    # Render text
    logria.current_end = 0
    logria.messages = constants.CREATE_SESSION_START_MESSAGES
    logria.previous_render = None  # Force render
    logria.render_text_in_output()

    # Get the user choice
    choice = None
    while choice not in {'file', 'command'}:
        logria.activate_prompt()
        choice = logria.box.gather().strip()
        if choice == ':q':
            logria.stop()
            break

    done = False
    logria.messages = []
    temp_session = SessionHandler()  # The session object we build
    while not done:
        if choice == 'file':
            done = handle_create_session_file(logria, temp_session)
        elif choice == 'command':
            done = handle_create_session_command(logria, temp_session)
        elif choice == ':q':
            logria.stop()
            break
        else:
            raise ValueError(f'{choice} not one of ("file", "command")')
    logria.setup_streams()


def handle_create_parser(logria: 'Logria') -> None:  # type: ignore
    """
    Get user input to create a session
    """
    temp_parser = Parser()

    # Render text
    logria.current_end = 0
    logria.messages = constants.CREATE_PARSER_MESSAGES
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    # Get type
    logria.activate_prompt()
    parser_type: str = ''
    while parser_type not in {'regex', 'split'}:
        logria.activate_prompt()
        parser_type = logria.box.gather().strip()
        if parser_type == ':q':
            logria.stop()
            return

    # Handle next step
    logria.messages = [f'Parser type {parser_type}']
    logria.messages.append(constants.PARSER_SET_NAME)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    # Get name
    logria.activate_prompt()
    parser_name = logria.box.gather().strip()
    if parser_name == ':q':
        logria.stop()
        return

    # Handle next step
    logria.messages.append(f'Parser name {parser_name}')
    logria.messages.append(constants.PARSER_SET_EXAMPLE)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    # Get example
    logria.activate_prompt()
    parser_example = logria.box.gather().strip()
    if parser_example == ':q':
        logria.stop()
        return

    # Handle next step
    logria.messages.append(f'Parser example {parser_example}')
    logria.messages.append(constants.PARSER_SET_PATTERN)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    # Get pattern
    logria.activate_prompt()
    parser_pattern = logria.box.gather()
    if parser_pattern == ':q':
        logria.stop()
        return

    # Set the parser's data
    temp_parser.set_pattern(
        parser_pattern, parser_type, parser_name, parser_example, {})

    # Determine the analytics dict
    parts = temp_parser.parse(parser_example)
    analytics = {part: 'count' for part in parts}

    # Set the parser's data with analytics
    temp_parser.set_pattern(
        parser_pattern, parser_type, parser_name, parser_example, analytics)

    logria.messages = temp_parser.as_list()
    logria.messages.append(constants.SAVE_CURRENT_PATTERN)
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    logria.activate_prompt()
    final_res = logria.box.gather().strip()
    if final_res == ':q':
        return
    temp_parser.save()
    logria.messages = []


def config_mode(logria: 'Logria') -> None:  # type: ignore
    """
    Start the configuration setup
    """
    logria.current_end = 0
    logria.messages = constants.CONFIG_START_MESSAGES
    logria.previous_render = None  # Force render
    logria.render_text_in_output()
    choice = None
    while choice not in {'session', 'parser'}:
        logria.activate_prompt()
        choice = logria.box.gather().strip()
        if choice == ':q':
            logria.stop()
            break
    if choice == 'session':
        handle_create_session(logria)
    elif choice == 'parser':
        handle_create_parser(logria)
