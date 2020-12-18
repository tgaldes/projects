from unittest.mock import MagicMock, Mock
import unittest
import test.TestConfig
from framework.Actions import *

class LabelActionTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LabelActionTest, self).__init__(*args, **kwargs)
        self.label_one = '"label one"'
        self.label_one_unwrapped = self.label_one[1:-1]
        self.label_two = '"label two " + match(0)'
        self.label_three = '"label three " + match(1)'
        self.matches = ['first match', 'second match']

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            la = LabelAction('')

    def test_set_label_no_matches(self):
        la = LabelAction(self.label_one)
        thread = Mock()
        thread.set_label = MagicMock()
        la.process(thread, [])
        thread.set_label.assert_called_once_with(self.label_one_unwrapped, unset=False)

    def test_set_label_with_match(self):
        la = LabelAction(self.label_two)
        thread = Mock()
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label two ' + self.matches[0], unset=False)

        la = LabelAction(self.label_three)
        thread = Mock()
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label three ' + self.matches[1], unset=False)

    def test_unset_label(self):
        la = LabelAction(self.label_two, unset=True)
        thread = Mock()
        thread.set_label = MagicMock()
        la.process(thread, self.matches)
        thread.set_label.assert_called_once_with('label two ' + self.matches[0], unset=True)

class DraftActionTest(unittest.TestCase):

    def test_no_body_or_destinations_specified(self):
        mock_thread = Mock()
        mock_thread.append_to_draft = MagicMock()
        mock_thread.set_label = MagicMock()
        da = DraftAction('', '')
        da.process(mock_thread, [])
        mock_thread.append_to_draft.assert_called_once_with('', [])

    def test_add_draft_no_matches(self):
        mock_thread = Mock()
        email = ['destination@abc.com']
        mock_thread.append_to_draft = MagicMock()
        mock_thread.default_reply = MagicMock(return_value=email)
        mock_thread.short_name = MagicMock(return_value='school')
        mock_thread.set_label = MagicMock()
        da = DraftAction('"Formatting a message with the short name: {}".format(thread.short_name())', 'thread.default_reply()')
        da.process(mock_thread, [])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.short_name.assert_called_once_with()
        mock_thread.append_to_draft.assert_called_once_with('Formatting a message with the short name: school', email)

        # Make sure we've added the automation label
        mock_thread.set_label.assert_called_once_with('automation', unset=False)

    def test_convert_destinations_from_string_to_list(self):
        mock_thread = Mock()
        email = 'destination@abc.com'
        mock_thread.append_to_draft = MagicMock()
        mock_thread.short_name = MagicMock(return_value='school')
        mock_thread.set_label = MagicMock()
        da = DraftAction('"Formatting a message with the short name: {}".format(thread.short_name())', '"{}"'.format(email))
        da.process(mock_thread, [])
        mock_thread.short_name.assert_called_once_with()
        mock_thread.append_to_draft.assert_called_once_with('Formatting a message with the short name: school', [email])
        
    def test_add_draft_with_matches(self):
        mock_thread = Mock()
        email = ['destination@abc.com']
        mock_thread.append_to_draft = MagicMock()
        mock_thread.default_reply = MagicMock(return_value=email)
        mock_thread.set_label = MagicMock()
        da = DraftAction('"Formatting a message with the short name: {}".format(match(1))', 'thread.default_reply()')
        da.process(mock_thread, ['match a', 'match b'])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.append_to_draft.assert_called_once_with('Formatting a message with the short name: match b', email)

        # Make sure we've added the automation label
        mock_thread.set_label.assert_called_once_with('automation', unset=False)

    def test_preprend_mode(self):
        mock_thread = Mock()
        email = ['destination@abc.com']
        mock_thread.prepend_to_draft = MagicMock()
        mock_thread.default_reply = MagicMock(return_value=email)
        mock_thread.set_label = MagicMock()
        da = DraftAction('"Formatting a message with the short name: {}".format(match(1))', 'thread.default_reply()', prepend=True)
        da.process(mock_thread, ['match a', 'match b'])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.prepend_to_draft.assert_called_once_with('Formatting a message with the short name: match b', email)


class MockThread(unittest.TestCase):
    def __init__(self, d, service, *args, **kwargs):
        super(MockThread, self).__init__(*args, **kwargs)
        self.thread = d;
        self.service = service
        self.get_short_name = MagicMock(return_value='USC')
        self.default_reply = MagicMock(return_value='tgaldes@gmail.com')
        self.append_to_draft = MagicMock()

    def __del__(self):
        self.append_to_draft.assert_called_once_with(unittest.mock.ANY, unittest.mock.ANY)
        self.default_reply.assert_called_once_with()
        self.get_short_name.assert_called_once_with()

class RedirectActionTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            ra = RedirectAction('', 'exp', 'exp')
        with self.assertRaises(Exception):
            ra = RedirectAction('exp', '', 'exp')
        with self.assertRaises(Exception):
            ra = RedirectAction('exp', 'exp', '')

    # This tests the flow the RedirectAction sees when we get a new rental application
    # 1 The application goes to tyler@ inbox
    # 2 We decode the email to get the email for the tenant who applied
    # 3 We find that thread in the apply inbox
    # 4 We send an email to that thread letting them know they need to approve it on their end
    def test_process_new_application(self):
        # set up inbox, thread that triggers the action, thread that we'll send a reply to
        mock_input_thread = Mock()
        mock_input_thread.get_new_application_email = MagicMock(return_value='tgaldes@gmail.com')
        mock_inbox = Mock()
        mock_inbox.get_service = MagicMock(return_value='service')
        mock_output_thread = Mock()
        mock_inbox.get_threads_from_email_address = MagicMock(return_value=[mock_output_thread])
        finder_expression = 'inbox.get_threads_from_email_address(thread.get_new_application_email())'
        destinations = 'thread.default_reply()'
        expression = '"You\'ll need to approve the application for housing at {} on your end".format(thread.get_short_name())'

        ra = RedirectAction(mock_inbox, finder_expression, expression, destinations)
        ra.process(mock_input_thread, ())
        mock_input_thread.get_new_application_email.assert_called_once_with()
        mock_inbox.get_threads_from_email_address.assert_called_once_with('tgaldes@gmail.com')
        self.assertEqual(1, mock_output_thread.append_to_draft.call_count)

class RemoveDraftActionTest(unittest.TestCase):

    def test_basic(self):
        rda = RemoveDraftAction()
        thread = Mock()
        thread.remove_existing_draft = MagicMock()
        rda.process(thread, ())
        thread.remove_existing_draft.assert_called_once_with()


class EmptyActionTest(unittest.TestCase):

    def test_basic(self):
        ea = EmptyAction()
        # Do nothing!
        ea.process(None, None)
        

class AttachmentActionTest(unittest.TestCase):

    def test_basic(self):
        eval_dest = 'tgaldes@gmail.com,another@asdf.com'
        dest = '"' + eval_dest + '"'
        fa = AttachmentAction(dest)
        thread = Mock()
        last_message = 'last message'
        attachment_data = 'data'
        attachment_fn = 'fn'
        thread.last_attachment = MagicMock(return_value=(attachment_data, attachment_fn))
        thread.add_attachment_to_draft = MagicMock()
        fa.process(thread, ())
        thread.add_attachment_to_draft.assert_called_once_with(attachment_data, attachment_fn, eval_dest)

