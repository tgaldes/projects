from unittest.mock import MagicMock, Mock
import unittest
import os

import test.TestConfig
from framework.Actions import *
from TestUtil import parent_path

from framework.Config import Config


class LabelActionTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LabelActionTest, self).__init__(*args, **kwargs)
        self.label_one = 'label one'
        self.label_two = 'label two'

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            la = LabelAction('')

    def test_set_label_no_matches(self):
        la = LabelAction(self.label_one)
        thread = Mock()
        thread.set_label = MagicMock()
        la.process(thread, [])
        thread.set_label.assert_called_once_with(self.label_one, unset=False)

    def test_unset_label(self):
        la = LabelAction(self.label_two, unset=True)
        thread = Mock()
        thread.set_label = MagicMock()
        la.process(thread, [])
        thread.set_label.assert_called_once_with('label two', unset=True)

class DraftActionTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(DraftActionTest, self).__init__(*args, **kwargs)
        self.config_dict = {'long_signature' : 'This is a long signature', 'short_signature' : 'short sig'}
        self.config = Config()
        self.config.initialize(None, self.config_dict)

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
        da = DraftAction('"Formatting a message with the signature: {}".format(Config()["long_signature"])', 'thread.default_reply()')
        da.process(mock_thread, [])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.append_to_draft.assert_called_once_with(f'Formatting a message with the signature: {self.config["long_signature"]}', email)

        # Make sure we've added the automation label
        mock_thread.set_label.assert_called_once_with('automation', unset=False)

    def test_preprend_mode(self):
        mock_thread = Mock()
        email = ['destination@abc.com']
        mock_thread.prepend_to_draft = MagicMock()
        mock_thread.default_reply = MagicMock(return_value=email)
        mock_thread.set_label = MagicMock()
        da = DraftAction('"Formatting a message with the signature: {}".format(Config()["long_signature"])', 'thread.default_reply()', prepend=True)
        da.process(mock_thread, [])
        mock_thread.default_reply.assert_called_once_with()
        mock_thread.prepend_to_draft.assert_called_once_with('Formatting a message with the signature: {}'.format(self.config["long_signature"]), email)


'''class MockThread(unittest.TestCase):
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
        self.get_short_name.assert_called_once_with()'''

class RedirectActionTest(unittest.TestCase):

    def test_throw_on_empty_init(self):
        with self.assertRaises(Exception):
            ra = RedirectAction('exp', '', 'exp')

    # This tests the flow the RedirectAction sees when we get a new rental application
    # 1 The application goes to tyler@ inbox
    # 2 We decode the email to get the email for the tenant who applied
    # 3 We find that thread in the apply inbox
    # 4 We send an email to that thread letting them know they need to approve it on their end
    def test_process_new_application(self):
    # TODO: update with new inbox mocks
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

        inner_action = DraftAction(expression, destinations)
        ra = RedirectAction(mock_inbox, finder_expression, inner_action)
        ra.process(mock_input_thread, ())
        mock_input_thread.get_new_application_email.assert_called_once_with()
        mock_inbox.get_threads_from_email_address.assert_called_once_with('tgaldes@gmail.com')
        self.assertEqual(1, mock_output_thread.append_to_draft.call_count)

class LabelLookupTest(unittest.TestCase):

    def test_set_label_from_other_inbox(self):
        mock_input_thread = Mock()
        mock_input_thread.get_new_application_name = MagicMock(return_value='Tyler Galdes')
        mock_inbox = Mock()
        mock_inbox.get_service = MagicMock(return_value='service')
        mock_output_thread = Mock()
        expected_label = 'Schools/USC'
        mock_output_thread.labels = MagicMock(return_value=['one', 'two', expected_label, 'three'])
        mock_inbox.query = MagicMock(return_value=[mock_output_thread])
        finder_expression = 'inbox.query(thread.get_new_application_name())'
        expression = 'Schools/.*'

        ra = LabelLookupAction(mock_inbox, finder_expression, expression)
        ra.process(mock_input_thread, ())
        mock_input_thread.get_new_application_name.assert_called_once_with()
        mock_inbox.query.assert_called_once_with('Tyler Galdes')
        mock_input_thread.set_label.assert_called_once_with(expected_label)


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
        
# Attach files based on the name of a glob
class AttachmentActionTest(unittest.TestCase):

    def test_basic(self):
        eval_dest = 'tgaldes@gmail.com,another@asdf.com'
        dest = '"' + eval_dest + '"'
        fns = [os.path.join(parent_path, 'attachments', 'one.png'), os.path.join(parent_path, 'attachments', 'two.png')]
        val = '"' + os.path.join(parent_path, 'attachments', '*png') + '"'
        fa = AttachmentAction(val, dest)
        thread = Mock()
        fa.process(thread, ())
        self.assertEqual(2, thread.add_attachment_to_draft.call_count)

        data_one, fn_one, emails = thread.add_attachment_to_draft.call_args_list[0][0]
        self.assertEqual(fns[0], fn_one)
        self.assertEqual(b'test one\n', data_one)
        data_two, fn_two, emails = thread.add_attachment_to_draft.call_args_list[1][0]
        self.assertEqual(fns[1], fn_two)
        self.assertEqual(b'test two\n', data_two)

class ForwardAttachmentActionTest(unittest.TestCase):

    def test_basic(self):
        eval_dest = 'tgaldes@gmail.com,another@asdf.com'
        eval_list = eval_dest.split(',')
        dest = '"' + eval_dest + '"'
        fa = ForwardAttachmentAction(dest)
        thread = Mock()
        last_message = 'last message'
        attachment_data = 'data'
        attachment_fn = 'fn'
        thread.last_attachment = MagicMock(return_value=(attachment_data, attachment_fn))
        thread.add_attachment_to_draft = MagicMock()
        fa.process(thread, ())
        thread.add_attachment_to_draft.assert_called_once_with(attachment_data, attachment_fn, eval_list)


'''def initialize():
    try:
        os.remove(ShellActionTest.output_fn)
    except:
        pass
class ShellActionTest(unittest.TestCase):
    script_dir = 'shell_test_scripts'
    output_fn = '/tmp/shell_action_test_output.txt'
    def test_success(self):
        initialize()
        command = '"/bin/sh ' + os.path.join(parent_path, ShellActionTest.script_dir, 'ok.sh') + '"'
        sa = ShellAction(command)

        thread = Mock()
        matches = []
        self.assertEqual(0, sa.process(thread, matches))

        with open(ShellActionTest.output_fn, 'r') as f:
            # file gives us a newline
            self.assertEqual('Hello, world!', f.read().strip())

    # The script we try to run here does have exe perms
    def test_failure(self):
        initialize()
        command = '"/bin/sh ' + os.path.join(parent_path, ShellActionTest.script_dir, 'error.sh') + '"'
        sa = ShellAction(command)

        thread = Mock()
        matches = []
        self.assertEqual(13, sa.process(thread, matches))
            
    def test_evaluate(self):
        initialize()
        ret = 'I expect this in the file'
        command = '"/bin/sh ' + os.path.join(parent_path, ShellActionTest.script_dir, 'evaluate.sh') + ' {}"'.format(ret)
        sa = ShellAction(command)

        thread = Mock()
        thread.default_reply = MagicMock(return_value=ret)
        matches = []
        self.assertEqual(0, sa.process(thread, matches))


        with open(ShellActionTest.output_fn, 'r') as f:
            # file gives us a newline
            self.assertEqual(ret, f.read().strip())'''
