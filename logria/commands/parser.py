"""
Commands for enabling parser and analytics
"""


import time
from json import JSONDecodeError

from logria.commands.regex import reset_regex_status
from logria.logger.parser import Parser

# from logria.communication.shell_output import Logria


def setup_parser(logria: 'Logria'):  # type: ignore
    """
    Setup a parser object in the main runtime
    """
    # Reset the status for new writes
    logria.reset_parser()
    reset_regex_status(logria)

    # Store previous message pointer
    if logria.messages is logria.stderr_messages:
        logria.previous_messages = logria.stderr_messages
    elif logria.messages is logria.stdout_messages:
        logria.previous_messages = logria.stdout_messages

    # Stick to top to show options
    logria.manually_controlled_line = False
    logria.stick_to_bottom = True
    logria.stick_to_top = False

    # Overwrite the messages pointer
    logria.messages = Parser().show_patterns()
    logria.previous_render = None
    logria.render_text_in_output()
    while True:
        time.sleep(logria.poll_rate)
        logria.activate_prompt()
        command = logria.box.gather().strip()
        if command == 'q':
            logria.reset_parser()
            return
        else:
            try:
                parser = Parser()
                parser.load(Parser().patterns()[int(command)])
                break
            except JSONDecodeError as err:
                logria.messages.append(
                    f'Invalid JSON: {err.msg} on line {err.lineno}, char {err.colno}')
            except ValueError:
                pass

    # Overwrite a different list this time, and reset it when done
    logria.messages = parser.display_example()
    logria.previous_render = None
    logria.render_text_in_output()
    while True:
        time.sleep(logria.poll_rate)
        logria.activate_prompt()
        command = logria.box.gather().strip()
        if command == 'q':
            logria.reset_parser()
            return
        else:
            try:
                command = int(command)
                assert command < len(logria.messages)
                logria.parser_index = int(command)
                logria.current_status = f'Parsing with {parser.get_name()}, field {parser.get_analytics_for_index(command)}'
                logria.write_to_command_line(logria.current_status)
                break
            except ValueError:
                pass
            except AssertionError:
                pass

    # Set parser
    logria.parser = parser

    # Put pointer back to new list
    logria.messages = logria.parsed_messages

    # Render immediately
    logria.previous_render = None

    # Stick to bottom again
    logria.last_index_processed = 0
    logria.stick_to_bottom = True
    logria.stick_to_top = False


def enable_parser(logria: 'Logria'):  # type: ignore
    """
    Enable parser
    """
    if logria.parser is not None:
        logria.reset_parser()
    setup_parser(logria)


def enable_analytics(logria: 'Logria'):  # type: ignore
    """
    Enable analytics engine
    """
    if logria.parser is not None:
        logria.last_index_processed = 0
        logria.parser.reset_analytics()
        if logria.analytics_enabled:
            logria.current_status = f'Parsing with {logria.parser.get_name()}, field {logria.parser.get_analytics_for_index(logria.parser_index)}'
            logria.parsed_messages = []
            logria.analytics_enabled = False
        else:
            logria.analytics_enabled = True
            logria.current_status = f'Parsing with {logria.parser.get_name()}, analytics view'


def teardown_parser(logria: 'Logria'):  # type: ignore
    """
    Tear down parser
    """
    logria.reset_parser()
