"""
Tests the app launcher
"""

import os
import unittest

from logria.commands import scroll
from logria.communication.render import determine_position
from logria.communication.shell_output import Logria
from logria.logger.processor import process_matches
from logria.utilities import regex_generator
from logria.utilities.keystrokes import resolve_keypress


class TestCanRenderContentRange(unittest.TestCase):
    """
    Tests scenarios with which we render content
    """

    def test_can_render_matches(self):
        """
        Test we render properly when using matches
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [f'{x}|{x}' for x in range(20)]

        # Set fake filter
        app.func_handle = regex_generator.regex_test_generator(r'\d\|\d')
        process_matches(app)

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = False

        start, end = determine_position(app, app.matched_rows)
        self.assertEqual(start, -1)
        self.assertEqual(end, 6)
        app.stop()

    def test_render_final_items(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = True

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 91)
        self.assertEqual(end, 99)
        app.stop()

    def test_render_first_items(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 6)
        app.stop()

    def test_render_few_items_from_middle(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 2  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(4)]

        # Set positional booleans
        app.manually_controlled_line = True
        app.stick_to_top = False
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 3)
        app.stop()

    def test_render_middle_items(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = True
        app.stick_to_top = False
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 72)
        self.assertEqual(end, 80)
        app.stop()

    def test_render_middle_items_early(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 5  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = True
        app.stick_to_top = False
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 5)
        app.stop()

    def test_render_small_list_from_top(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 0  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(5)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 4)
        app.stop()

    def test_render_small_list_from_bottom(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 0  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(5)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = True

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 4)
        app.stop()

    def test_render_scroll_up(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 99  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = True

        # Scroll action
        scroll.up(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 90)
        self.assertEqual(end, 98)
        app.stop()

    def test_render_scroll_down(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 10  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        scroll.down(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 3)
        self.assertEqual(end, 11)
        app.stop()

    def test_render_scroll_down_matched(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 10  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]
        app.matched_rows = [x for x in range(20)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        scroll.down(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 3)
        self.assertEqual(end, 11)
        app.stop()

    def test_render_stick_bottom(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = False

        # Scroll action
        scroll.bottom(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 91)
        self.assertEqual(end, 99)
        app.stop()

    def test_render_scroll_past_end(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 101  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = True
        app.stick_to_top = False
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 92)
        self.assertEqual(end, 100)
        app.stop()

    def test_render_everything_unset(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 101  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = False

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 92)
        self.assertEqual(end, 100)
        app.stop()

    def test_render_stick_top(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = True

        # Scroll action
        scroll.top(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 6)
        app.stop()

    def test_render_scroll_pgdn(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 10  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        scroll.pgdn(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 9)
        self.assertEqual(end, 17)
        app.stop()

    def test_render_scroll_pgup(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 40  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        scroll.pgup(app)

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 25)
        self.assertEqual(end, 33)
        app.stop()


class TestCanRenderContentRangeKeypress(unittest.TestCase):
    """
    Tests scenarios with which we render content
    """

    def test_render_scroll_up_keypress(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 99  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = True

        # Scroll action
        resolve_keypress(app, 'KEY_UP')

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 90)
        self.assertEqual(end, 98)
        app.stop()

    def test_render_scroll_down_keypress(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 10  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        resolve_keypress(app, 'KEY_DOWN')

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 3)
        self.assertEqual(end, 11)
        app.stop()

    def test_render_stick_bottom_keypress(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = False

        # Scroll action
        resolve_keypress(app, 'KEY_RIGHT')

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 91)
        self.assertEqual(end, 99)
        app.stop()

    def test_render_stick_top_keypress(self):
        """
        Test we render properly when stuck to the top
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 80  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = False
        app.stick_to_bottom = True

        # Scroll action
        resolve_keypress(app, 'KEY_LEFT')

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, -1)
        self.assertEqual(end, 6)
        app.stop()

    def test_render_scroll_pgdn_keystroke(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 10  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        resolve_keypress(app, 'KEY_NPAGE')

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 9)
        self.assertEqual(end, 17)
        app.stop()

    def test_render_scroll_pgup_keystroke(self):
        """
        Test we render properly when stuck to the bottom
        """
        os.environ['TERM'] = 'dumb'
        app = Logria(None, False, False)

        # Fake window size: 10 x 100
        app.height = 10
        app.width = 100

        # Set fake previous render
        app.last_row = app.height - 3  # simulate the last row we can render to
        app.current_end = 40  # Simulate the last message rendered

        # Set fake messages
        app.messages = [str(x) for x in range(100)]

        # Set positional booleans
        app.manually_controlled_line = False
        app.stick_to_top = True
        app.stick_to_bottom = True

        # Scroll action
        resolve_keypress(app, 'KEY_PPAGE')

        start, end = determine_position(app, app.messages)
        self.assertEqual(start, 25)
        self.assertEqual(end, 33)
        app.stop()
