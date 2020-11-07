from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
from Thread import Thread
import pathlib
import os
import json
import pdb
from contextlib import contextmanager
import pudb
from email.mime.text import MIMEText
import base64
import NewLogger



# global config
NewLogger.global_log_level = 'DEBUG' # TODO: use the TestConfig module
parent_path = str(pathlib.Path(__file__).parent.absolute())

def dict_from_fn(fn):
    with open(fn, 'r') as f:
        return json.load(f)

def encode_for_payload(text):
    return base64.urlsafe_b64encode(text.encode('utf-8')).decode()

class ThreadTest(unittest.TestCase):

    def test_field(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/make_them_say_no.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)
        # Will grab the 'To' field from the first message in thread
        self.assertEqual('apply@cf-ld.com', thread.field('To'))
        # Will grab the 'To' field from the last message in thread
        self.assertEqual('tonyma@uchicago.edu', thread.field('To', subset=thread.field('messages')[-1]))

    def test_one_email_thread(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/one_email_thread.txt'))
        mock_service = Mock()
        mock_service.get_label_id = MagicMock(return_value='mockid')
        mock_service.set_label = MagicMock(return_value={'messages' : [], 'labelIds' : ['IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX', 'mockid']})
        thread = Thread(d, mock_service)
        id = thread.field('id')
        self.assertEqual('test subject', thread.subject())
        mock_service.get_email = MagicMock(return_value='tyler@cf-ld.com')
        self.assertEqual(['tgaldes@gmail.com'], thread.default_reply())
        mock_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        self.assertEqual(['tgaldes@gmail.com'], thread.default_reply())
        self.assertEqual('', thread.existing_draft_text())
        self.assertEqual(None, thread.existing_draft_id())
        self.assertEqual(False, thread.has_existing_draft())
        self.assertFalse(thread.is_last_message_from_us())
        self.assertEqual('first message\r\n<div dir="ltr">first message</div>\r\n', thread.last_message_text())

        # setting a label and updating threads internal state with new label ids
        thread.set_label('test label string')
        mock_service.set_label.assert_called_once_with(id, mock.ANY)
        mock_service.get_label_id.assert_called_once_with('test label string')
        self.assertTrue('mockid' in thread.field('labelIds'))

        # unset a label
        thread.set_label('test label string', unset=True)
        mock_service.set_label.assert_called_with(id, {'addLabelIds' : [], 'removeLabelIds' : ['mockid']})
        mock_service.get_label_id.assert_called_with('test label string')


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
        mock_service.append_or_create_draft = MagicMock(return_value={'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg), 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}})
        thread.append_to_draft(first_msg, ['tgaldes@gmail.com'])
        # now when we want to add text to the draft we should append to it
        mock_service.append_or_create_draft = MagicMock(return_value={'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg + second_msg), 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}})
        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        thread.append_to_draft(second_msg, ['tgaldes@gmail.com'])
        self.assertEqual(first_msg + second_msg, thread.existing_draft_text())
        self.assertEqual(draft_id, thread.existing_draft_id())
        self.assertEqual(True, thread.has_existing_draft())
        # When the thread ends with a draft from us, we should not use 
        # that to say the last message is from us
        self.assertFalse(thread.is_last_message_from_us())
        # Nor should we get the text of the draft
        self.assertEqual('first message\r\n<div dir="ltr">first message</div>\r\n', thread.last_message_text())

        # try to set a label that doesn't exist, we want an exception
        with self.assertRaises(Exception):
            mock_service.get_label_id = MagicMock(return_value=None)
            thread.set_label('this label doesn\'t exist')

    def test_new_application_email(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/new_application.txt'))
        mock_service = Mock()
        mock_service.get_label_id = MagicMock(return_value='mockid')
        mock_service.set_label = MagicMock(return_value={'messages' : [], 'labelIds' : ['IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX', 'mockid']})
        thread = Thread(d, mock_service)
        self.assertEqual('kimaquinosmc@gmail.com', thread.get_new_application_email())

    def test_last_ts(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/make_them_say_no.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)
        self.assertEqual(1604097866, thread.last_ts())

    def test_labels(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/make_them_say_no.txt'))
        mock_service = Mock()
        ln = 'label_name'
        mock_service.get_label_name = MagicMock(return_value=ln)
        thread = Thread(d, mock_service)
        self.assertEqual([ln for x in range(4)], thread.labels())

    # Not currently part of public interface
    def test_no_last_message(self):
        pass

    def test_short_name(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/make_them_say_no.txt'))
        mock_service = Mock()
        mock_service.get_label_name = MagicMock(return_value='Schools/USC')
        thread = Thread(d, mock_service)
        self.assertEqual('USC', thread.short_name())
        mock_service.get_label_name = MagicMock(return_value='not a school label')
        self.assertEqual('the campus', thread.short_name())
        self.assertTrue(thread.is_last_message_from_us())

    def test_short_name(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/make_them_say_no.txt'))
        mock_service = Mock()
        mock_service.get_label_name = MagicMock(return_value='Schools/USC')
        thread = Thread(d, mock_service)
        self.assertEqual('USC', thread.short_name())
        mock_service.get_label_name = MagicMock(return_value='not a school label')
        self.assertEqual('the campus', thread.short_name())

    def test_new_desintations_match_existing_draft(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)
        first_msg = 'draft line one'
        with self.assertRaises(Exception):
            thread.append_to_draft('draft msg', ['nottheexistingdraftemail@asdf.com'])

    def test_make_them_say_no(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/make_them_say_no.txt'))
        mock_service = Mock()
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_label_name = MagicMock(return_value='Schools/USC')
        thread = Thread(d, mock_service)
        # Evening of 20201030
        self.assertEqual(1604097866, thread.last_ts())
        one_day_in_future = thread.last_ts() + 86400
        two_days_in_future = thread.last_ts() + 86400 * 2
        self.assertEqual('USC', thread.short_name())
        mock_service.get_label_name = MagicMock(return_value='not a school label')
        self.assertEqual('the campus', thread.short_name())
        self.assertEqual('Hi Tony,\r\n\r\nWe actually only do UCLA for summer housing.\r\n\r\nBest,\r\nTyler\r\nCF&LD\r\n', thread.last_message_text())

        # check out timestamp boolean expression
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: thread.last_ts()))
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: one_day_in_future))
        self.assertTrue(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: two_days_in_future))

        # check it out when our email isn't the last in the thread
        mock_service.get_email = MagicMock(return_value='tenant@gmail.com')
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: thread.last_ts()))
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: one_day_in_future))
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: two_days_in_future))

    def test_append_creates_response_to_last_message_in_thread(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/message_from_tenant_then_message_from_us.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)
        self.assertEqual('Hi Rawaa,\r\n\r\nHow long would you want to stay for? We could sign until Mid May right now.\r\n$650 a month, move in 1/4/21, 4.5 months of rent.\r\n\r\nTyler', thread.last_message_text())
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        mock_service.append_or_create_draft = MagicMock(return_value={'snippet': first_msg, 'internalDate': '1604543785000', 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(first_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': '26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f', 'historyId': '803631', 'sizeEstimate': 755})
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')

        # append the draft
        thread.append_to_draft(first_msg, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        message = MIMEText(first_msg, 'html')
        message['to'] = '26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com'
        message['from'] = 'apply@cleanfloorslockingdoors.com'
        message['subject'] = 'Re: Early Termination'
        message['In-Reply-To'] = "<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>"
        message['References'] = "<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>"
        payload = {'message' : {'threadId' : thread.field('id'), 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
        # do the asserts
        # None passed as the draft id since we don't have an existing draft in this test case
        mock_service.append_or_create_draft.assert_called_once_with(payload, None)
        self.assertEqual(first_msg, thread.existing_draft_text())
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        self.assertEqual(draft_id, thread.existing_draft_id())


        # now when we want to add text to the draft we should append to it
        mock_service.append_or_create_draft = MagicMock(return_value={'snippet': first_msg, 'internalDate': '1604543785000', 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(first_msg + second_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name':'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': '26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f', 'historyId': '803631', 'sizeEstimate': 755})
        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        thread.append_to_draft(second_msg, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        message = MIMEText(first_msg + second_msg, 'html')
        message['to'] = '26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com'
        message['from'] = 'apply@cleanfloorslockingdoors.com'
        message['subject'] = 'Re: Early Termination'
        message['In-Reply-To'] = "<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>"
        message['References'] = "<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>"
        payload = {'message' : {'threadId' : thread.field('id'), 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
        mock_service.append_or_create_draft.assert_called_once_with(payload, draft_id)
        self.assertEqual(first_msg + second_msg, thread.existing_draft_text())
        self.assertEqual(draft_id, thread.existing_draft_id())
        self.assertEqual('Hi Rawaa,\r\n\r\nHow long would you want to stay for? We could sign until Mid May right now.\r\n$650 a month, move in 1/4/21, 4.5 months of rent.\r\n\r\nTyler', thread.last_message_text())


    def test_append_to_existing_draft_supplied_by_service(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        existing_text = 'this is a draft used for testing purposes'
        mock_service.append_or_create_draft = MagicMock(return_value={'snippet': existing_text + first_msg, 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(existing_text + first_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': 'pulkitagarwalcs@gmail.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f'})
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])

        # append the draft
        thread.append_to_draft(first_msg, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        message = MIMEText(existing_text + first_msg, 'html')
        message['to'] = 'pulkitagarwalcs@gmail.com'
        message['from'] = 'apply@cleanfloorslockingdoors.com'
        message['subject'] = 'New submission for SJSU'
        message['In-Reply-To'] = "<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>"
        message['References'] = "<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>"
        payload = {'message' : {'threadId' : thread.field('id'), 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
        # do the asserts
        mock_service.append_or_create_draft.assert_called_once_with(payload, draft_id)
        self.assertEqual(existing_text + first_msg, thread.existing_draft_text())
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        self.assertEqual(draft_id, thread.existing_draft_id())
        self.assertEqual('Hi Pulkit,', thread.salutation()) 


        # when we want to add text to the draft we should still be appending to it
        mock_service.append_or_create_draft = MagicMock(return_value={'snippet': existing_text + first_msg, 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(existing_text + first_msg + second_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': 'pulkitagarwalcs@gmail.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f'})
        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        thread.append_to_draft(second_msg, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        message = MIMEText(existing_text + first_msg + second_msg, 'html')
        message['to'] = 'pulkitagarwalcs@gmail.com'
        message['from'] = 'apply@cleanfloorslockingdoors.com'
        message['subject'] = 'New submission for SJSU'
        message['In-Reply-To'] = "<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>"
        message['References'] = "<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>"
        payload = {'message' : {'threadId' : thread.field('id'), 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
        mock_service.append_or_create_draft.assert_called_once_with(payload, draft_id)
        self.assertEqual(existing_text + first_msg + second_msg, thread.existing_draft_text())
        self.assertEqual(draft_id, thread.existing_draft_id())

    # google is nice enough to put a decoded snippet of the message body
    # in it's own field, but to be legit we want to be decoding the whole
    # message from the payload
    def test_read_message_body_from_decoded_payload(self):
        self.maxDiff = None
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/existing_draft_too_big_for_snippet.txt'))
        expected_decoded_payload = 'the following is a long message\r\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\r\ncccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\r\ndddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd\r\n'
        mock_service = Mock()
        thread = Thread(d, mock_service)
        self.assertEqual(expected_decoded_payload, thread.existing_draft_text())


# TODO: ut for special characters returned by service in message body? some are translating & and ' like unicode

    def test_reply_all(self):
        # Last message in thread is tyler -> George, cc Tim and Micah
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/reply_all.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)
        mock_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        # george is the to, mharrel and tim are both cced
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())
        self.assertEqual(['gbremer@yahoo.com'], thread.default_reply(reply_all=False))
        # Now we'll have sent the last message To all three (not cced)
        headers = thread.thread['messages'][-1]['payload']['headers']
        for i, pair in enumerate(headers):
            if pair['name'] == 'Cc':
                del headers[i]
            elif pair['name'] == 'To':
                pair['value'] += ',Micah Harrel <mharrel@jhtechnologies.com>, Tim Simmons <tim@overdrivenotes.com>'

        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply(reply_all=False))

        # Now we'll remove the last message in the thread
        thread.thread['messages'].pop()
        headers = thread.thread['messages'][-1]['payload']['headers']
        # Last message is from George -> Tyler, Tim, Micah
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply(reply_all=False))
        for i, pair in enumerate(headers):
            if pair['name'] == 'To':
                pair['value'] = 'Tyler Galdes <tyler@cleanfloorslockingdoors.com>'
        headers.append({'name' : 'Cc' , 'value' : 'Micah Harrel <mharrel@jhtechnologies.com>, Tim Simmons <tim@overdrivenotes.com>'})
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())
        # Now that tim and micah are ccs we will skip them if we don't want to reply all
        self.assertEqual(['gbremer@yahoo.com'], thread.default_reply(reply_all=False))

        # Now we load a thread that specifies a Reply-To header
        # we want to pick up that and not use the from field
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/one_message_with_reply_to.txt'))
        thread = Thread(d, mock_service)
        self.assertEqual(['1he4ezedq4zcji4ahg9r6wxjc25@convo.hotpads.com'], thread.default_reply())
        self.assertEqual(['1he4ezedq4zcji4ahg9r6wxjc25@convo.hotpads.com'], thread.default_reply(reply_all=False))

    def test_salutation(self):
        # get from email we sent
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/html_encoded_message_from_us.txt'))
        mock_service = Mock()
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        thread = Thread(d, mock_service)
        self.assertEqual('Hi Samah,', thread.salutation())
        # get from reply-to field
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/one_message_with_reply_to.txt'))
        thread = Thread(d, mock_service)
        self.assertEqual('Hi Kimberly,', thread.salutation())
        # default
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/new_application.txt'))
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        thread = Thread(d, mock_service)
        self.assertEqual('Hi,', thread.salutation())
        
    def test_remove_existing_draft(self):
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/one_email_thread.txt'))
        mock_service = Mock()
        thread = Thread(d, mock_service)

        # With no draft, we shouldn't do anything on the service
        thread.remove_existing_draft()

        # Now we'll get a thread that has an existing draft
        d = dict_from_fn(os.path.join(parent_path, 'thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'))
        mock_service = Mock()
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        mock_service.delete_draft = MagicMock()

        thread = Thread(d, mock_service)
        thread.remove_existing_draft()
        mock_service.delete_draft.assert_called_once_with(draft_id)
        self.assertFalse(thread.has_existing_draft())







