"""
Processors functions to filter messages from Logria streams
"""


# from logria.communication.shell_output import Logria


def process_matches(logria: 'Logria') -> None:  # type: ignore
    """
    Process the matches for filtering, should by async but the commented code here
    does not work

    # TODO: Fix this method
    """
    # def add_to_list(result: multiprocessing.Queue, messages: list, last_idx_searched: int, func_handle: Callable):
    #     """
    #     Main loop will create this separate process to find matches while the main loop runs
    #     """
    #     for index, message in range(last_idx_searched, len(messages)):
    #         print(index, message)
    #         if func_handle(message):
    #             result.put(index)
    #         return result

    # result = multiprocessing.Queue()
    # proc = multiprocessing.Process(target=add_to_list, args=(result, logria.messages, logria.last_index_searched, logria.func_handle))
    # proc.start()
    # proc.join()
    # print('done')
    # logria.last_index_searched = len(logria.messages)
    # while not result.empty:
    #     idx = result.get()
    #     print(idx)
    #     logria.matched_rows.append(idx)
    # logria.write_to_prompt('in method')

    # For each message, add its index to the list of matches; this is more efficient than
    # Storing a second copy of each match
    for index in range(logria.last_index_regexed, len(logria.messages)):
        # pylint: disable=not-callable
        if logria.func_handle and logria.func_handle(logria.messages[index]):
            logria.matched_rows.append(index)
    logria.last_index_regexed = len(logria.messages)


def process_parser(logria: 'Logria'):  # type: ignore
    """
    Load parsed messages to new array if we have matches

    # TODO: Same as process_matches
    """
    for index in range(logria.last_index_processed, len(logria.previous_messages)):
        if logria.analytics_enabled:
            logria.parser.handle_analytics_for_message(
                logria.previous_messages[index])
            logria.messages = logria.parser.analytics_to_list()
            # For some reason this isn't switching back
            logria.last_index_processed = len(logria.previous_messages)
        else:
            if logria.messages is not logria.parsed_messages:
                logria.messages = logria.parsed_messages
            match = logria.parser.parse(logria.previous_messages[index])
            if match:
                try:
                    logria.parsed_messages.append(match[logria.parser_index])
                except IndexError:
                    # If there was an error parsing, the message did not match the current pattern
                    pass
            logria.last_index_processed = len(logria.messages)
