from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
from Thread import Thread
#from GMailService import GMailService # TODO: constructor of this is expensive so we want to create a straight mock
import json
import pdb

def dict_from_fn(fn):
    with open(fn, 'r') as f:
        return json.load(f)

class ThreadTest(unittest.TestCase):
    '''def __init__(self, *args, **kwargs):
        super(ThreadTest, self).__init__(*args, **kwargs)
        self.label_one = '"label one"'
        self.label_one_unwrapped = self.label_one[1:-1]
        self.label_two = '"label two " + match(0)'
        self.label_three = '"label three " + match(1)'
        self.matches = ['first match', 'second match']'''

    def test_one_email_thread(self):
        d = dict_from_fn('./test/thread_test_inputs/one_email_thread.txt')
        mock_service = Mock()
        mock_service.get_label_id = MagicMock(return_value='mockid')
        mock_service.set_label = MagicMock()
        thread = Thread(d, mock_service)
        id = thread.field('id')
        self.assertEqual('test subject', thread.subject())
        self.assertEqual('tgaldes@gmail.com', thread.default_reply())
        self.assertEqual('', thread.existing_draft_text())
        self.assertEqual(None, thread.existing_draft_id())

        thread.set_label('test label string')
        mock_service.set_label.assert_called_once_with(id, mock.ANY)
        mock_service.get_label_id.assert_called_once_with('test label string')

