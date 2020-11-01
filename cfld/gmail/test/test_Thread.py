from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
from Thread import Thread
import json
import pdb
from contextlib import contextmanager
import pudb

@contextmanager
def postmortem_pudb():
    try:
        yield
    except:
        yield

def dict_from_fn(fn):
    with open(fn, 'r') as f:
        return json.load(f)

class ThreadTest(unittest.TestCase):

    def test_one_email_thread(self):
        #with postmortem_pudb():
        d = dict_from_fn('./test/thread_test_inputs/one_email_thread.txt')
        mock_service = Mock()
        mock_service.get_label_id = MagicMock(return_value='mockid')
        mock_service.set_label = MagicMock(return_value={'messages' : [], 'labelIds' : ['IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX', 'mockid']})
        thread = Thread(d, mock_service)
        id = thread.field('id')
        self.assertEqual('test subject', thread.subject())
        self.assertEqual(['tgaldes@gmail.com'], thread.default_reply())
        self.assertEqual('', thread.existing_draft_text())
        self.assertEqual(None, thread.existing_draft_id())

        # setting a label and updating threads internal state with new label ids
        thread.set_label('test label string')
        mock_service.set_label.assert_called_once_with(id, mock.ANY)
        mock_service.get_label_id.assert_called_once_with('test label string')
        self.assertTrue('mockid' in thread.field('labelIds'))

        # getting some fields from various depths of the json 
        self.assertEqual('690981', thread.field('historyId'))
        self.assertEqual('Thu, 29 Oct 2020 21:49:56 -0400', thread.field('Date')) # from the first message object
        self.assertEqual('test subject', thread.field('Subject'))
        self.assertEqual('1604022596000', thread.field('internalDate'))

        # add a brand new draft
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        mock_service.append_or_create_draft = MagicMock(return_value={'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT']})
        thread.append_to_draft(first_msg, ['tgaldes@gmail.com'])
        # now when we want to add text to the draft we should append to it
        mock_service.append_or_create_draft = MagicMock(return_value={'id' : draft_msg_id, 'snippet' : first_msg + second_msg, 'labelIds' : ['DRAFT']})
        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        thread.append_to_draft(second_msg, ['tgaldes@gmail.com'])
        self.assertEqual(first_msg + second_msg, thread.existing_draft_text())
        self.assertEqual(draft_id, thread.existing_draft_id())

        # try to set a label that doesn't exist, we want an exception
        with self.assertRaises(Exception):
            mock_service.get_label_id = MagicMock(return_value=None)
            thread.set_label('this label doesn\'t exist')

    def test_new_application_email(self):
        d = dict_from_fn('./test/thread_test_inputs/new_application.txt')
        mock_service = Mock()
        mock_service.get_label_id = MagicMock(return_value='mockid')
        mock_service.set_label = MagicMock(return_value={'messages' : [], 'labelIds' : ['IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX', 'mockid']})
        thread = Thread(d, mock_service)
        self.assertEqual('kimaquinosmc@gmail.com', thread.get_new_application_email())

    def test_make_them_say_no(self):
        d = dict_from_fn('./test/thread_test_inputs/make_them_say_no.txt')
        mock_service = Mock()
        #mock_service.get_label_id = MagicMock(return_value='mockid')
        #mock_service.set_label = MagicMock(return_value={'messages' : [], 'labelIds' : ['IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX', 'mockid']})
        thread = Thread(d, mock_service)
        self.assertEqual("1604097866000", thread.last_ts())

