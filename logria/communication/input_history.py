"""
Class to handle keeping track of input history
"""
from typing import List


class HistoryTape():
    """
    Class to keep track of user's input history
    """

    def __init__(self):
        self.history_tape: List[str] = []  # Not a real queue
        self.current_index: int = -1  # The index we are at in the queue

    def size(self) -> int:
        """
        Return the number of items in the tape
        """
        return len(self.history_tape)

    def get_current_item(self) -> str:
        """
        Get the most recent item
        """
        if not self.history_tape:
            return ''
        return self.history_tape[self.current_index]

    def go_to(self, index: int) -> str:
        """
        Go to a specific point in time, bound by the size of the tape
        """
        if index >= 0 and index < len(self.history_tape) - 1:
            self.current_index = index
        elif index > len(self.history_tape):
            self.current_index = len(self.history_tape) - 1
        elif index < 0:
            self.current_index = 0
        return self.get_current_item()

    def tail(self, last_n: int = 5) -> List[str]:
        """
        Get the most recent `last n` messages from the tape
        """
        if last_n < 0:
            return []
        return self.history_tape[-last_n:]

    def add_item(self, item: str) -> None:
        """
        Add's the current item to the end of the queue and update the index
        """
        self.history_tape.append(item)
        self.current_index = len(self.history_tape) - 1

    def scroll_back_n(self, num_to_scroll: int) -> str:
        """
        Scroll back one item in the tape
        """
        if self.history_tape:
            self.current_index = max(0, self.current_index - num_to_scroll)
        return self.get_current_item()

    def scroll_forward_n(self, num_to_scroll: int) -> str:
        """
        Scroll forward one item in the tape
        """
        if self.history_tape:
            self.current_index = min(
                len(self.history_tape) - 1, self.current_index + num_to_scroll)
        return self.get_current_item()

    def scroll_back(self) -> str:
        """
        Common case where we scroll back a single item
        """
        return self.scroll_back_n(1)

    def scroll_forward(self) -> str:
        """
        Common case where we scroll back a single item
        """
        return self.scroll_forward_n(1)

    def __repr__(self):
        return f'<History Tape containing {self.size():,} items, currently selected {self.get_current_item()}>'
