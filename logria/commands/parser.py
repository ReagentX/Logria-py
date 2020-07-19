"""
Commands for enabling parser and analytics
"""


import time
from json import JSONDecodeError

from logria.commands.regex import reset_regex_status
from logria.logger.parser import Parser

# from logria.communication.shell_output import Logria


def reset_parser(logria: 'Logria'):  # type: ignore
    """
    Remove the current parser, if any exists
    """
    if logria.func_handle:
        logria.current_status = f'Regex with pattern /{logria.regex_pattern}/'
    else:
        logria.current_status = 'No filter applied'  # CLI message, rendered after
    if logria.previous_messages:
        # Move messages pointer to the previous state
        if logria.previous_messages is logria.stderr_messages:
            logria.messages = logria.stderr_messages
        else:
            logria.messages = logria.stdout_messages
        logria.previous_messages = []
        logria.parsed_messages = []  # Dump parsed messages
    logria.parser = None  # Dump the parser
    logria.analytics_enabled = False  # Disable analytics blocker
    logria.parser_index = 0  # Dump the pattern index
    logria.last_index_processed = 0  # Reset the last searched index
    logria.current_end = 0  # We now do not know where to end
    logria.stick_to_bottom = True  # Stay at the bottom for the next render
    logria.stick_to_top = False  # Do not stick to the top
    logria.manually_controlled_line = False  # Do not stop rendering new messages
    logria.write_to_command_line(logria.current_status)


def setup_parser(logria: 'Logria'):  # type: ignore
    """
    Setup a parser object in the main runtime
    """
    # Reset the status for new writes
    reset_parser(logria)
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
        if command == ':q':
            parser = None
            break
        try:
            parser = Parser()
            parser.load(Parser().patterns()[int(command)])
            break
        except JSONDecodeError as err:
            logria.messages.append(
                f'Invalid JSON: {err.msg} on line {err.lineno}, char {err.colno}')
        except ValueError:
            pass

    # Ensure we didn't exit early already
    if parser:
        # Overwrite a different list this time, and reset it when done
        logria.messages = parser.display_example()
        logria.previous_render = None
        logria.render_text_in_output()
        while True:
            time.sleep(logria.poll_rate)
            logria.activate_prompt()
            command = logria.box.gather().strip()
            if command == ':q':
                reset_parser(logria)
                break
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
    else:
        reset_parser(logria)

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
        reset_parser(logria)
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
    reset_parser(logria)
