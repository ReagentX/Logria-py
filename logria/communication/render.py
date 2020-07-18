"""
Functions to handler rendering content in the Logria window
"""


from math import ceil
from typing import List, Tuple

from logria.utilities.regex_generator import get_real_length

# from logria.communication.shell_output import Logria


def determine_position(logria: 'Logria', messages_pointer: List[str]) -> Tuple[int, int]:  # type: ignore
    """
    Determine the start and end positions for a screen render
    """
    if logria.stick_to_top:
        end = 0
        rows = 0
        for i in messages_pointer:
            if messages_pointer is logria.messages:
                # No processing needed for normal messages
                item: str = i
            elif messages_pointer is logria.matched_rows:
                # Grab the matched message
                item = logria.messages[i]  # type: ignore
            # Determine if the message will fit in the window
            msg_lines = ceil(get_real_length(item) / logria.width)
            rows += msg_lines
            # If we can fit, increment the last row number
            if rows < logria.last_row and end < len(messages_pointer) - 1:
                end += 1
            else:
                break
        logria.current_end = end  # Save this row so we know where we are
        # When iterating backwards, we need to end at 0, so we must create a range
        # object like range(10, -1, -1) to generate a list that ends at 0
        # If there are no messages, we want to not iterate later, so we change the
        # -1 to 0 so that we do not iterate at all
        return -1 if messages_pointer else 0, end  # Early escape
    elif logria.stick_to_bottom:
        end = len(messages_pointer) - 1
    elif logria.manually_controlled_line:
        if len(messages_pointer) < logria.last_row:
            # If have fewer messages than lines, just render it all
            end = len(messages_pointer) - 1
        elif logria.current_end < logria.last_row:
            # If the last row we rendered comes before the last row we can render,
            # use all of the available rows
            end = logria.current_end
        elif logria.current_end < len(messages_pointer):
            # If we are looking at a valid line, render ends there
            end = logria.current_end
        else:
            # If we have over-scrolled, go back
            if logria.current_end > len(messages_pointer):
                logria.current_end = len(messages_pointer)
            # Since current_end can be zero, we have to use the number of messages
            end = len(messages_pointer)
    else:
        end = len(messages_pointer)
    logria.current_end = end  # Save this row so we know where we are
    # Last index of a list is length - 1
    start = max(-1, end - logria.last_row - 1)
    return start, end
