from unittest.mock import MagicMock, Mock
import unittest
from Actions import *
from Thread import Thread
import NewLogger
NewLogger.global_log_level = 'DEBUG'

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
        thread.set_label.assert_called_once_with(self.label_one_unwrapped, unset=False)

    def test_set_label_with_match(self):
        la = LabelAction(self.label_two)
        thread = Thread({}, None)
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label two ' + self.matches[0], unset=False)

        la = LabelAction(self.label_three)
        thread = Thread({}, None)
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label three ' + self.matches[1], unset=False)

    def test_unset_label(self):
        la = LabelAction(self.label_two, unset=True)
        thread = Thread({}, None)
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label two ' + self.matches[0], unset=True)

class DraftActionTest(unittest.TestCase):
    def test_add_draft_no_matches(self):
        mock_thread = Mock()
        email = ['destination@abc.com']
        mock_thread.append_to_draft = MagicMock()
        mock_thread.default_reply = MagicMock(return_value=email)
        mock_thread.short_name = MagicMock(return_value='school')
        mock_thread.set_label = MagicMock()
        da = DraftAction('thread.default_reply()', '"Formatting a message with the short name: {}".format(thread.short_name())')
        da.process(mock_thread, [])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.short_name.assert_called_once_with()
        mock_thread.append_to_draft.assert_called_once_with(email, 'Formatting a message with the short name: school')

        # Make sure we've added the automation label
        mock_thread.set_label.assert_called_once_with('automation', unset=False)
        
    def test_add_draft_with_matches(self):
        mock_thread = Mock()
        email = ['destination@abc.com']
        mock_thread.append_to_draft = MagicMock()
        mock_thread.default_reply = MagicMock(return_value=email)
        mock_thread.set_label = MagicMock()
        da = DraftAction('thread.default_reply()', '"Formatting a message with the short name: {}".format(match(1))')
        da.process(mock_thread, ['match a', 'match b'])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.append_to_draft.assert_called_once_with(email, 'Formatting a message with the short name: match b')

        # Make sure we've added the automation label
        mock_thread.set_label.assert_called_once_with('automation', unset=False)

