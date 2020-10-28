"""
Handle creating input streams for Logria
"""


import time
from json import JSONDecodeError
from os.path import isfile
from typing import List

from logria.commands.config import config_mode, resolve_delete_command
from logria.communication.input_handler import (CommandInputStream,
                                                FileInputStream)
from logria.utilities import constants
from logria.utilities.command_parser import Resolver
from logria.utilities.session import SessionHandler

# from logria.communication.shell_output import Logria


def render_setup_messages(logria: 'Logria', session_handler: SessionHandler) -> None:  # type: ignore
    """
    Render setup messages from session_handler
    """
    # Create a new message list to see
    setup_messages: List[str] = []
    logria.messages = setup_messages
    # Tell the user what we are doing
    setup_messages.extend(constants.START_MESSAGE)
    setup_messages.extend(session_handler.show_sessions())

    # Force re-render
    logria.redraw()


def setup_streams(logria: 'Logria') -> None:  # type: ignore
    """
    When launched without a stream, allow the user to define them for us
    """
    # Setup a SessionHandler and get the existing saved sessions
    session_handler = SessionHandler()
    render_setup_messages(logria, session_handler)

    # Create resolver class to resolve commands
    resolver = Resolver()

    # Get user input
    while True:
        time.sleep(logria.poll_rate)
        logria.activate_prompt()
        command = logria.box.gather().strip()
        if not command:
            continue
        if command == ':q':
            logria.stop()
            break
        if ':r ' in command[:3]:
            items_to_remove = resolve_delete_command(command)
            sessions = session_handler.sessions()
            for item in items_to_remove:
                if item in sessions:
                    session_handler.remove_session(sessions[item])
            render_setup_messages(logria, session_handler)
            continue
        try:
            chosen_item = int(command)
            session = session_handler.load_session(chosen_item)
            if not session:
                continue
            stored_commands = session['commands']
            # Commands need a type
            for stored_command in stored_commands:
                if session.get('type') == 'file':
                    logria.streams.append(FileInputStream(stored_command))
                elif session.get('type') == 'command':
                    logria.streams.append(CommandInputStream(stored_command))
        except KeyError as err:
            logria.messages.append(
                f'Data missing from configuration: {err}')
            logria.render_text_in_output()
            continue
        except JSONDecodeError as err:
            logria.messages.append(
                f'Invalid JSON: {err.msg} on line {err.lineno}, char {err.colno}')
            logria.render_text_in_output()
            continue
        except ValueError:
            if command == ':config':
                config_mode(logria)
                return
            elif command == ':q':
                logria.stop()
            elif isfile(command):
                logria.streams.append(
                    FileInputStream(command.split('/')))
                session_handler.save_session(
                    'File - ' + command.replace('/', '|'), [command.split('/')], 'file')
            else:
                cmd = resolver.resolve_command_as_list(command)
                logria.streams.append(CommandInputStream(cmd))
                session_handler.save_session(
                    'Cmd - ' + command.replace('/', '|'), cmd, 'command')
        break

    # Launch the subprocess
    for stream in logria.streams:
        stream.poll_rate = logria.poll_rate
        stream.start()

    # Set status back to what it was
    logria.write_to_command_line(logria.current_status)

    # Render immediately
    logria.previous_render = None

    # Reset messages
    logria.stderr_messages = []
    logria.messages = logria.stderr_messages
