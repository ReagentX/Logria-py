"""
Commands for enabling parser and analytics
"""


# from logria.communication.shell_output import Logria

def enable_parser(logria: 'Logria'):
    """
    Enable parser
    """
    if logria.parser is not None:
        logria.reset_parser()
    logria.setup_parser()


def enable_analytics(logria: 'Logria'):
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


def teardown_parser(logria: 'Logria'):
    """
    Tear down parser
    """
    logria.reset_parser()
