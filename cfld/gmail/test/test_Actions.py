from unittest.mock import MagicMock, Mock
import unittest
from Actions import *
from Thread import Thread

class LabelActionTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LabelActionTest, self).__init__(*args, **kwargs)
        self.label_one = '"label one"'
        self.label_one_unwrapped = self.label_one[1:-1]
        self.label_two = '"label two " + match(0)'
        self.label_three = '"label three " + match(1)'
        self.matches = ['first match', 'second match']

    def test_set_label_no_matches(self):
        la = LabelAction(self.label_one)
        thread = Thread({}, None)
        thread.set_label = MagicMock()
        la.process(thread, [])
        thread.set_label.assert_called_once_with(self.label_one_unwrapped)

    def test_set_label_with_match(self):
        la = LabelAction(self.label_two)
        thread = Thread({}, None)
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label two ' + self.matches[0])

        la = LabelAction(self.label_three)
        thread = Thread({}, None)
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label three ' + self.matches[1])

class DraftActionTest(unittest.TestCase):
    def test_set_label_no_matches(self):
        print('TODO')
        pass
    def test_set_label_with_match(self):
        print('TODO')
        pass

