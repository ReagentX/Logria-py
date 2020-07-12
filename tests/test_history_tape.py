"""
Unit Tests for history tape
"""

import unittest

from logria.communication import input_history


class TestHistoryTapeFunctions(unittest.TestCase):
    """
    Test cases to ensure history tape are the expected values
    """

    def test_can_create_history_tape(self):
        """
        Test that we can create a history tape instance without a cache
        """
        tape = input_history.HistoryTape(use_cache=False)
        self.assertIsInstance(tape, input_history.HistoryTape)

    def test_cah_create_cache_history_tape(self):
        """
        Test that we can create a history tape instance with a cache
        """
        tape = input_history.HistoryTape()
        tape.add_item('Test')
        self.assertIsInstance(tape, input_history.HistoryTape)

    def test_get_current_item_empty(self):
        """
        Test that we don't crash when looking at a blank tape
        """
        tape = input_history.HistoryTape(use_cache=False)
        self.assertEqual(tape.get_current_item(), '')

    def test_can_add_item(self):
        """
        Test that we can add and retrieve the current item
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test')
        self.assertEqual(tape.get_current_item(), 'Test')

    def test_cant_add_excluded_item(self):
        """
        Test that we can add and retrieve the current item
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item(':history')
        tape.add_item(':history off')
        self.assertEqual(tape.size(), 0)

    def test_at_end(self):
        """
        Test that we correctly report when we are at the end
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test')
        self.assertTrue(tape.at_end())

    def test_not_at_end(self):
        """
        Test that we correctly report when we are not at the end
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.scroll_back()
        tape.scroll_back()
        self.assertFalse(tape.at_end())

    def test_cant_add_item_twice(self):
        """
        Test that we can add and retrieve the current item
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test')
        tape.add_item('Test')
        self.assertEqual(tape.size(), 1)

    def test_can_scroll_backward_in_bounds(self):
        """
        Ensure we can scroll back
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.scroll_back()
        tape.scroll_back()
        self.assertEqual(tape.get_current_item(), 'Test 2')

    def test_can_scroll_backward_out_of_bounds(self):
        """
        Ensure we can scroll back
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.scroll_back()
        tape.scroll_back()
        tape.scroll_back()
        tape.scroll_back()
        self.assertEqual(tape.get_current_item(), 'Test 1')

    def test_can_scroll_forward_in_bounds_(self):
        """
        Ensure we can scroll forward
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.scroll_back()
        tape.scroll_back()
        tape.scroll_forward()
        self.assertEqual(tape.get_current_item(), 'Test 3')

    def test_can_scroll_forward_in_bounds(self):
        """
        Ensure we can scroll forward
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.scroll_back()
        tape.scroll_back()
        tape.scroll_forward()
        tape.scroll_forward()
        tape.scroll_forward()
        tape.scroll_forward()
        tape.scroll_forward()
        self.assertEqual(tape.get_current_item(), 'Test 3')

    def test_can_go_to_in_bounds(self):
        """
        Ensure we can go to a point in the tape in bounds
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.go_to(0)
        self.assertEqual(tape.get_current_item(), 'Test 1')

    def test_can_go_to_out_of_bounds_up(self):
        """
        Ensure we do not try to go to a point above the tape and instead go to the last item
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.go_to(10)
        self.assertEqual(tape.get_current_item(), 'Test 3')

    def test_can_go_to_out_of_bounds_down(self):
        """
        Ensure we do not try to go to a point below the tape and instead go to the first item
        """
        tape = input_history.HistoryTape(use_cache=False)
        tape.add_item('Test 1')
        tape.add_item('Test 2')
        tape.add_item('Test 3')
        tape.go_to(-3)
        self.assertEqual(tape.get_current_item(), 'Test 1')

    def test_tape_size(self):
        """
        Test that we can get size of the tape
        """
        tape = input_history.HistoryTape(use_cache=False)
        self.assertEqual(tape.size(), 0)
        for item in range(10):
            tape.add_item(f'Test {item}')
        self.assertEqual(tape.size(), 10)

    def test_can_tail_default_n(self):
        """
        Test that we can get the last 5 messages
        """
        tape = input_history.HistoryTape(use_cache=False)
        num_to_get = 5
        for item in range(10):
            tape.add_item(f'Test {item}')
        self.assertEqual(
            tape.tail(),
            [f'Test {x + (tape.size() - num_to_get)}' for x in range(5)]
        )

    def test_can_tail_custom_end(self):
        """
        Test that we can get the last n messages
        """
        tape = input_history.HistoryTape(use_cache=False)
        num_to_get = 7
        for item in range(10):
            tape.add_item(f'Test {item}')
        self.assertEqual(
            tape.tail(num_to_get),
            [f'Test {x + (tape.size() - num_to_get)}' for x in range(num_to_get)]
        )
