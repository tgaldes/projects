from unittest.mock import MagicMock, Mock
from unittest import mock
import unittest
import pdb

from test.TestUtil import get_thread_constructor_args, encode_for_payload
import test.TestConfig

from framework.Thread import Thread
from services.gmail.GMailMessage import GMailMessage


class ThreadTest(unittest.TestCase):

    def test_one_email_thread(self):
        mock_service = Mock()
        mock_service.get_label_id = MagicMock(return_value='mockid')
        mock_service.set_label = MagicMock(return_value=['IMPORTANT', 'CATEGORY_PERSONAL', 'INBOX', 'mockid'])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_email_thread.txt'), mock_service)
        id = thread.identifier
        self.assertEqual('test subject', thread.subject())
        mock_service.get_user = MagicMock(return_value='tyler')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        self.assertEqual(['tgaldes@gmail.com'], thread.default_reply())
        mock_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='tyler')
        self.assertEqual(['tgaldes@gmail.com'], thread.default_reply())
        self.assertEqual('', thread.existing_draft_text())
        self.assertEqual(None, thread.existing_draft_id())
        self.assertEqual(False, thread.has_draft())
        self.assertFalse(thread.is_last_message_from_us())
        self.assertEqual('first message\r\n<div dir="ltr">first message</div>\r\n', thread.last_message_text())

        # setting a label and updating threads internal state with new label ids
        thread.set_label('test label string')
        mock_service.set_label.assert_called_once_with(id, mock.ANY, False)
        mock_service.get_label_id.assert_called_once_with('test label string')
        self.assertTrue('mockid' in thread.label_ids())

        # unset a label
        mock_service.get_label_name = MagicMock(return_value='test label string')
        thread.set_label('test label string', unset=True)
        mock_service.set_label.assert_called_with(id, 'mockid', True)
        mock_service.get_label_id.assert_called_with('test label string')


        # getting some fields from various depths of the json 
        self.assertEqual('test subject', thread.subject())
        self.assertEqual(1604022596, thread.last_ts())

        # add a brand new draft
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg)}, 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}, {}))
        thread.append_to_draft(first_msg, ['tgaldes@gmail.com'])
        # now when we want to add text to the draft we should append to it
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg + second_msg)}, 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}, {}))
        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        thread.append_to_draft(second_msg, ['tgaldes@gmail.com'])
        self.assertEqual(first_msg + second_msg, thread.existing_draft_text())
        self.assertEqual(draft_id, thread.existing_draft_id())
        self.assertEqual(True, thread.has_draft())
        # When the thread ends with a draft from us, we should not use 
        # that to say the last message is from us
        self.assertFalse(thread.is_last_message_from_us())
        # Nor should we get the text of the draft
        self.assertEqual('first message\r\n<div dir="ltr">first message</div>\r\n', thread.last_message_text())

        # try to set a label that doesn't exist, we want to do nothing
        mock_service.get_label_id = MagicMock(return_value=None)
        nonexistent_label = 'doesnt exist'
        thread.set_label(nonexistent_label)
        self.assertFalse(nonexistent_label in thread.labels())


    def test_last_ts(self):
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/make_them_say_no.txt'), mock_service)
        self.assertEqual(1604097866, thread.last_ts())

    def test_labels(self):
        mock_service = Mock()
        ln = 'label_name'
        mock_service.get_label_name = MagicMock(return_value=ln)
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/make_them_say_no.txt'), mock_service)
        self.assertEqual([ln for x in range(4)], thread.labels())

    def test_new_destinations_match_existing_draft(self):
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        first_msg = 'draft line one'
        with self.assertRaises(Exception):
            thread.append_to_draft('draft msg', ['nottheexistingdraftemail@asdf.com'])

    def test_make_them_say_no(self):
        mock_service = Mock()
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        mock_service.get_label_name = MagicMock(return_value='Schools/USC')
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/make_them_say_no.txt'), mock_service)
        # Evening of 20201030
        self.assertEqual(1604097866, thread.last_ts())
        one_day_in_future = thread.last_ts() + 86400
        two_days_in_future = thread.last_ts() + 86400 * 2
        mock_service.get_label_name = MagicMock(return_value='not a school label')
        self.assertEqual('Hi Tony,\r\n\r\nWe actually only do UCLA for summer housing.\r\n\r\nBest,\r\nTyler\r\nCF&LD\r\n', thread.last_message_text())

        # check out timestamp boolean expression
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: thread.last_ts()))
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: one_day_in_future))
        self.assertTrue(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: two_days_in_future))

        # check it out when our email isn't the last in the thread
        mock_service.get_user = MagicMock(return_value='tenant')
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: thread.last_ts()))
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: one_day_in_future))
        self.assertFalse(thread.need_make_them_say_no(duration_days=1, time_getter_f=lambda: two_days_in_future))

    def test_append_creates_response_to_last_message_in_thread(self):
        mock_service = Mock()
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_from_us.txt'), mock_service)
        self.assertEqual('Hi Rawaa,\r\n\r\nHow long would you want to stay for? We could sign until Mid May right now.\r\n$650 a month, move in 1/4/21, 4.5 months of rent.\r\n\r\nTyler', thread.last_message_text())
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'snippet': first_msg, 'internalDate': '1604543785000', 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(first_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': '26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f', 'historyId': '803631', 'sizeEstimate': 755}, {}))
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])

        # append the draft
        thread.append_to_draft(first_msg, thread.default_reply())
        # do the asserts
        # None passed as the draft id since we don't have an existing draft in this test case
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertIsNone(called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com', mime_multipart['to'])
        self.assertEqual('Re: Early Termination', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>', mime_multipart['References'])
        # TODO: there's got to be a less hacky way to get the payload of attached MIME parts
        self.assertEqual(first_msg, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])
        self.assertEqual(first_msg, thread.existing_draft_text())


        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        self.assertEqual(draft_id, thread.existing_draft_id())


        # now when we want to add text to the draft we should append to it
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'snippet': first_msg, 'internalDate': '1604543785000', 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(first_msg + second_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name':'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': '26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f', 'historyId': '803631', 'sizeEstimate': 755}, {}))
        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        thread.append_to_draft(second_msg, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('26tgsdnx0e3adi2t8jx3gjgjaj1@convo.trulia.com', mime_multipart['to'])
        self.assertEqual('Re: Early Termination', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVXaBk=FFHjn-Ah3Px8XG+yrca9EiP1Y+DUYBq6YC5s0Lg@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(first_msg + second_msg, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])

        self.assertEqual(first_msg + second_msg, thread.existing_draft_text())
        self.assertEqual(draft_id, thread.existing_draft_id())
        self.assertEqual('Hi Rawaa,\r\n\r\nHow long would you want to stay for? We could sign until Mid May right now.\r\n$650 a month, move in 1/4/21, 4.5 months of rent.\r\n\r\nTyler', thread.last_message_text())


    def test_append_to_existing_draft_supplied_by_service(self):
        mock_service = Mock()
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        # We have already sent one email
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345' # This is the message id that we will load initially
        first_new_draft_msg_id = '3456' # When we update a draft, the draft id stays the same but the message id associated with that draft id changes ;)
        second_new_draft_msg_id = '4567'
        existing_text = 'this is a draft used for testing purposes'
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}]) # when we're mapping the msg id that we loaded to a draft id, return the original id
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'snippet': existing_text + first_msg, 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(existing_text + first_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': 'pulkitagarwalcs@gmail.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4, Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': first_new_draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f'}, {})) # Wehn we've done the update, we'll return a different msg id

        # append the draft
        thread.append_to_draft(first_msg, thread.default_reply())

        # do the asserts
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('pulkitagarwalcs@gmail.com', mime_multipart['to'])
        self.assertEqual('New submission for SJSU', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(existing_text + first_msg, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])
        self.assertEqual(existing_text + first_msg, thread.existing_draft_text())

        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : first_new_draft_msg_id}}])
        self.assertEqual(draft_id, thread.existing_draft_id())
        self.assertEqual('Hi Pulkit,', thread.salutation()) 


        # Remember that the draft object is a different object than the message with a different id
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : first_new_draft_msg_id}}, {'id' : 'not our id', 'message' : {'id' : 'not our message id'}}])
        # when we want to add text to the draft we should still be appending to it
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'snippet': existing_text + first_msg, 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(existing_text + first_msg + second_msg)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': \
        'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': 'pulkitagarwalcs@gmail.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', \
        'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': second_new_draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f'}, {}))

        # append the draft
        thread.append_to_draft(second_msg, thread.default_reply())
        # do the asserts
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('pulkitagarwalcs@gmail.com', mime_multipart['to'])
        self.assertEqual('New submission for SJSU', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(existing_text + first_msg + second_msg, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])
        self.assertEqual(existing_text + first_msg + second_msg, thread.existing_draft_text())
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : second_new_draft_msg_id}}, {'id' : 'not our id', 'message' : {'id' : 'not our message id'}}])
        self.assertEqual(draft_id, thread.existing_draft_id())

    # google is nice enough to put a decoded snippet of the message body
    # in it's own field, but to be legit we want to be decoding the whole
    # message from the payload
    def test_read_message_body_from_decoded_payload(self):
        self.maxDiff = None
        expected_decoded_payload = 'the following is a long message\r\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\r\ncccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\r\ndddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd\r\n'
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/existing_draft_too_big_for_snippet.txt'), mock_service)
        self.assertEqual(expected_decoded_payload, thread.existing_draft_text())

    def test_reply_all(self):
        # Last message in thread is tyler -> George, cc Tim and Micah
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/reply_all.txt'), mock_service)
        mock_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='tyler')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        # george is the to, mharrel and tim are both cced
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())
        self.assertEqual(['gbremer@yahoo.com'], thread.default_reply(reply_all=False))


        # Now tyler sent the last message To all three (not cced)
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/reply_all_two.txt'), mock_service)
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply(reply_all=False))

        # Last message is from George -> Tyler, Tim, Micah
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/reply_all_three.txt'), mock_service)
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply(reply_all=False))
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())

        # Now last is Geroge -> Tyler, cc: tim & michah
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/reply_all_four.txt'), mock_service)
        self.assertEqual(['gbremer@yahoo.com'], thread.default_reply(reply_all=False))
        self.assertEqual(['gbremer@yahoo.com', 'mharrel@jhtechnologies.com', 'tim@overdrivenotes.com'], thread.default_reply())

        # Now we load a thread that specifies a Reply-To header
        # we want to pick up that and not use the from field
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_message_with_reply_to.txt'), mock_service)
        self.assertEqual(['1he4ezedq4zcji4ahg9r6wxjc25@convo.hotpads.com'], thread.default_reply())
        self.assertEqual(['1he4ezedq4zcji4ahg9r6wxjc25@convo.hotpads.com'], thread.default_reply(reply_all=False))

    # TODO: we could use a unit test where the last message in the thread is from us
    # and doesn't have a salutation. The ut will confirm we're getting the salutation
    # from the first message our user sent
    def test_salutation(self):
        # get from email we sent
        mock_service = Mock()
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/html_encoded_message_from_us.txt'), mock_service)
        self.assertEqual('Hi Samah,', thread.salutation())
        # get from reply-to field
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_message_with_reply_to.txt'), mock_service)
        self.assertEqual('Hi Kimberly,', thread.salutation())
        # Our first email
        # default
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/new_application.txt'), mock_service)
        self.assertEqual('Hi,', thread.salutation())

        # some services send the field like 'Reply-to' (to is lowercase)
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_message_with_reply_to_lowercase.txt'), mock_service)
        self.assertEqual('Hi Kimberly,', thread.salutation())


    def test_prepend_to_draft(self):
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        existing_text = 'this is a draft used for testing purposes'
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'snippet': existing_text + first_msg, 'payload': {'mimeType': 'text/plain', 'body': {'size': 143, 'data': encode_for_payload(first_msg + existing_text)}, 'partId': '', 'filename': '', 'headers': [{'name': 'Received', 'value': 'from 1055564699329 named unknown by gmailapi.google.com with HTTPREST; Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Content-Type', 'value':'text/plain; charset="us-ascii"'}, {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}, {'name': 'to', 'value': 'pulkitagarwalcs@gmail.com'}, {'name': 'from', 'value': 'apply@cleanfloorslockingdoors.com'}, {'name': 'subject', 'value': 'New submission for SJSU'}, {'name': 'In-Reply-To', 'value': '<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'References', 'value':'<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>'}, {'name': 'Date', 'value': 'Wed, 4 Nov 2020 23:36:25 -0300'}, {'name': 'Message-Id', 'value': '<CAAD9TVXpvrS66uVpWOSwYogxA6cYb6_+Z2wYybh8HkqYcC0Ryw@mail.gmail.com>'}]}, 'id': draft_msg_id, 'labelIds': ['DRAFT'], 'threadId': '175704c1f999408f'}, {}))
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])

        # append the draft
        thread.prepend_to_draft(first_msg, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        # do the asserts
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('pulkitagarwalcs@gmail.com', mime_multipart['to'])
        self.assertEqual('New submission for SJSU', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(first_msg + existing_text, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])

    def test_add_attachments_to_existing_draft(self):
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        first_msg = 'draft line one'
        draft_id = '1234'
        draft_msg_id = '2345'
        existing_text = 'this is a draft used for testing purposes\r\n'
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}]) # when we're mapping the msg id that we loaded to a draft id, return the original id
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'threadId': '1762af1ef77adfbf', 'sizeEstimate': 18396, 'payload': {'parts': [{'parts': [{'filename': '', 'body': {'size': 4961, 'data': 'dGhpcyBpcyBhIGRyYWZ0IHVzZWQgZm9yIHRlc3RpbmcgcHVycG9zZXMNCg0KDQpPbiBGcmksIERlYyAxMSwgMjAyMCBhdCA3OjUzIFBNIEphdmllciBGZXJyZXIgPGphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tPiANCndyb3RlOg0KDQo-IFRoYW5rIFUgDQo-DQo-IE9uIEZyaSwgRGVjIDExLCAyMDIwIGF0IDc6NTIgUE0gQXBwbGljYXRpb24gVGVhbSA8DQo-IGFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbT4gd3JvdGU6DQo-DQo-PiBPayBzb3VuZHMgZ29vZCwgSSdsbCBmb3J3YXJkIGl0IHRvIHRoZSBwcm9wZXJ0eSBvd25lcnMuDQo-Pg0KPj4gQmVzdCwNCj4-IFR5bGVyDQo-PiBDRiZMRA0KPj4NCj4-DQo-PiBPbiBGcmksIERlYyAxMSwgMjAyMCBhdCA3OjI2IFBNIEphdmllciBGZXJyZXIgPGphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tPiANCj4-IHdyb3RlOg0KPj4NCj4-PiBJIHdhcyBjaGVja2luZyBteSBjcmVkaXQga2FybWEgYW5kIGluIGVmZmVjdCBJIGhhdmUgbXkgcHJldmlvdXMgYWRkcmVzcyANCj4-PiAyNTUgc3cgMTF0aCBzdCBhcHQgNDAyIHppcCAzMzEzMCBNaWFtaSBGbG9yaWRhIA0KPj4-IDxodHRwczovL3d3dy5nb29nbGUuY29tL21hcHMvc2VhcmNoLzI1NStzdysxMXRoK3N0K2FwdCs0MDIremlwKzMzMTMwK01pYW1pK0Zsb3JpZGE_ZW50cnk9Z21haWwmc291cmNlPWc-DQo-Pj4gIA0KPj4-DQo-Pj4gdGhlcmUgaXMgYSBwcm9ibGVtIHdpdGggdGhhdCA_Pw0KPj4-DQo-Pj4gU2VudCBmcm9tIG15IGlQaG9uZQ0KPj4-DQo-Pj4gT24gRGVjIDExLCAyMDIwLCBhdCAxMTo1MSBBTSwgSmF2aWVyIEZlcnJlciA8amF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb20-IA0KPj4-IHdyb3RlOg0KPj4-DQo-Pj4g77u_WWVzIGl04oCZcyBteSBzc24gODgyIC0gNTEgLTQzMzcgDQo-Pj4NCj4-PiBNeSBzc24gaGFzIGJlZW4gZm9yIDQgeWVhcnMuIEkgZG9uJ3QgdW5kZXJzdGFuZCB0aGUgcHJvYmxlbSwgY291bGQgeW91IA0KPj4-IGV4cGxhaW4gaXQgdG8gbWU_DQo-Pj4NCj4-PiBiZWNhdXNlIG9mIHRoZSBjb3ZpZCBJIGhhZCBwcm9ibGVtcyB3aXRoIG15IGNyZWRpdCBzY29yZSBidXQgSSBjYW4gc2hvdyANCj4-PiB5b3UgbXkgYWNjb3VudCBzdGF0ZW1lbnRzDQo-Pj4NCj4-PiBTZW50IGZyb20gbXkgaVBob25lDQo-Pj4NCj4-PiBPbiBEZWMgMTEsIDIwMjAsIGF0IDExOjQ0IEFNLCBBcHBsaWNhdGlvbiBUZWFtIDwNCj4-PiBhcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb20-IHdyb3RlOg0KPj4-DQo-Pj4g77u_DQo-Pj4gSGkgSmF2aWVyLA0KPj4-DQo-Pj4gQmVmb3JlIEkgZG8tIEkgaGF2ZSB0aGUgZm9sbG93aW5nIG5vdGUgaW4gdGhlIGNyZWRpdCByZXBvcnQgZnJvbSANCj4-PiBUcmFuc3VuaW9uLg0KPj4-DQo-Pj4gQ3VycmVudCBhZGRyZXNzIG1pc21hdGNoIC0gaW5wdXQgZG9lcyBub3QgbWF0Y2ggZmlsZS5TU04gbWF5IGJlIGludmFsaWQgDQo-Pj4gLSBpdCB3YXMgZWl0aGVyIHZlcnkgcmVjZW50bHkgb3IgbmV2ZXIgaXNzdWVkIGJ5IHRoZSBTb2NpYWwgU2VjdXJpdHkgDQo-Pj4gQWRtaW5pc3RyYXRpb24uDQo-Pj4gQ2FuIHlvdSBjb25maXJtIHRoYXQgdGhlIHNvY2lhbCB5b3UgZW50ZXJlZCB3YXMgY29ycmVjdD8gSWYgaXQgd2FzIA0KPj4-IHJlY2VudGx5IGlzc3VlZCBjb3VsZCB5b3UgZXhwbGFpbiB3aHkgYW5kIHN1Ym1pdCBzdXBwb3J0aW5nIGRvY3VtZW50YXRpb24_IA0KPj4-IEFzIGl0IHN0YW5kcyByaWdodCBub3cgYmFzZWQgb24gdGhlIHNvY2lhbCBudW1iZXIgYW5kIHRoZSBudW1iZXIgb2YgDQo-Pj4gY29sbGVjdGlvbnMgeW91J3ZlIGhhZCByZWNlbnRseSBJIHdvdWxkIHJlY29tbWVuZCB0byB0aGUgb3duZXJzIHRoYXQgdGhleSANCj4-PiBkbyBub3QgYXBwcm92ZSB5b3VyIGFwcGxpY2F0aW9uLg0KPj4-IEJlc3QsDQo-Pj4gVHlsZXINCj4-PiBDRiZMRA0KPj4-DQo-Pj4NCj4-PiBPbiBGcmksIERlYyAxMSwgMjAyMCBhdCAxMTozOCBBTSBBcHBsaWNhdGlvbiBUZWFtIDwNCj4-PiBhcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb20-IHdyb3RlOg0KPj4-DQo-Pj4-IE9rIGdyZWF0LiBJJ3ZlIGZvcndhcmRlZCB0aGUgcmVwb3J0cyB0byB0aGUgb3duZXJzIGZvciBhcHByb3ZhbC4NCj4-Pj4NCj4-Pj4gQmVzdCwNCj4-Pj4gVHlsZXINCj4-Pj4gQ0YmTEQNCj4-Pj4NCj4-Pj4NCj4-Pj4gT24gV2VkLCBEZWMgOSwgMjAyMCBhdCAxMDo0MiBQTSBKYXZpZXIgRmVycmVyIDwNCj4-Pj4gamF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb20-IHdyb3RlOg0KPj4-Pg0KPj4-Pj4gSSBoYWQgYSB0aWNrZXQgYmVjYXVzZSBvZiB0aGUgc2VhdGJlbHQgYnV0IHRoZSBqdWRnZSBkaXNtaXNzZWQgdGhlIA0KPj4-Pj4gY2FzZSAudGhlIHNlY29uZCBvbmUgZGVmaW5pdGVseSB3YXNu4oCZdCBtZQ0KPj4-Pj4NCj4-Pj4-IFNlbnQgZnJvbSBteSBpUGhvbmUNCj4-Pj4-DQo-Pj4-PiBPbiBEZWMgOSwgMjAyMCwgYXQgNzoyMSBQTSwgQXBwbGljYXRpb24gVGVhbSA8DQo-Pj4-PiBhcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb20-IHdyb3RlOg0KPj4-Pj4NCj4-Pj4-IO-7vw0KPj4-Pj4gSGkgSmF2aWVyLA0KPj4-Pj4NCj4-Pj4-IEluIHlvdXIgYXBwbGljYXRpb24gSSBzZWUgdHdvIGNyaW1pbmFsIHJlcG9ydHMgaW4gbWlhbWksIG9uZSByZWxhdGVkIA0KPj4-Pj4gdG8gZHJpdmluZyB3aXRob3V0IGEgc2VhdGJlbHQsIG9uZSBmb3IgdHJlc3Bhc3NpbmcuIEkgZG9uJ3QgdGhpbmsgZWl0aGVyIG9mIA0KPj4-Pj4gdGhvc2Ugd2lsbCBiZSBkZWFsYnJlYWtlcnMgZm9yIHRoZSBvd25lcnMsIGJ1dCBJJ20gcmVhY2hpbmcgb3V0IHRvIGFzayBpZiANCj4-Pj4-IHRoZXkgd2VyZSB5b3UuIFRoZSBsYXN0IG5hbWVzIG9uIGJvdGggYXJlIGRpZmZlcmVudCB0aGFuIHlvdXJzLCBidXQgdGhlIA0KPj4-Pj4gZmlyc3QgYW5kIG1pZGRsZSBuYW1lcyBtYXRjaC4NCj4-Pj4-DQo-Pj4-PiBCZXN0LA0KPj4-Pj4gVHlsZXINCj4-Pj4-IENGJkxEDQo-Pj4-Pg0KPj4-Pj4NCj4-Pj4-IE9uIFdlZCwgRGVjIDksIDIwMjAgYXQgNDozNSBQTSBKYXZpZXIgRmVycmVyIDwNCj4-Pj4-IGphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tPiB3cm90ZToNCj4-Pj4-DQo-Pj4-Pj4gSSBqdXN0IGZvdW5kZWQgdGhlIGVtYWlsIGFuZCBmaW5pc2hlZCB0aGUgdHJhbnNVbmlvbiBhcHBsaWNhdGlvbiANCj4-Pj4-Pg0KPj4-Pj4-DQo-Pj4-Pj4gT24gV2VkLCBEZWMgOSwgMjAyMCBhdCA0OjE5IFBNIEFwcGxpY2F0aW9uIFRlYW0gPA0KPj4-Pj4-IGFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbT4gd3JvdGU6DQo-Pj4-Pj4NCj4-Pj4-Pj4gSGkgSmF2aWVyLA0KPj4-Pj4-Pg0KPj4-Pj4-PiBUaGUgaW5mbyBJIGhhdmUgc2F5cyBpdCdzIGJlZW4gc2VudC4gUGxlYXNlIGNoZWNrIHlvdSBzcGFtIGZvbGRlci4NCj4-Pj4-Pj4NCj4-Pj4-Pj4gQmVzdCwNCj4-Pj4-Pj4gVHlsZXINCj4-Pj4-Pj4gQ0YmTEQNCj4-Pj4-Pj4NCj4-Pj4-Pj4NCj4-Pj4-Pj4gT24gV2VkLCBEZWMgOSwgMjAyMCBhdCAxMDoxNSBBTSBKYXZpZXIgRmVycmVyIDwNCj4-Pj4-Pj4gamF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb20-IHdyb3RlOg0KPj4-Pj4-Pg0KPj4-Pj4-Pj4gSeKAmW0gc29ycnkgYnV0LCBJIGRvbuKAmXQgaGF2ZSBhbnkgZW1haWwgZnJvbSB0cmFuc1VuaW9uLiANCj4-Pj4-Pj4-DQo-Pj4-Pj4-PiBTZW50IGZyb20gbXkgaVBob25lDQo-Pj4-Pj4-Pg0KPj4-Pj4-Pj4gT24gRGVjIDksIDIwMjAsIGF0IDEwOjA4IEFNLCBBcHBsaWNhdGlvbiBUZWFtIDwNCj4-Pj4-Pj4-IGFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbT4gd3JvdGU6DQo-Pj4-Pj4-Pg0KPj4-Pj4-Pj4g77u_DQo-Pj4-Pj4-PiBIaSBKYXZpZXIsDQo-Pj4-Pj4-Pg0KPj4-Pj4-Pj4gUGxlYXNlIGxvb2sgZm9yIGFuIGVtYWlsIGZyb20gVHJhbnN1bmlvbi4NCj4-Pj4-Pj4-DQo-Pj4-Pj4-PiBUeWxlcg0KPj4-Pj4-Pj4NCj4-Pj4-Pj4-IE9uIFR1ZSwgRGVjIDgsIDIwMjAgYXQgNjowNiBQTSBKYXZpZXIgRmVycmVyIDwNCj4-Pj4-Pj4-IGphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tPiB3cm90ZToNCj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gSSdtIHNvcnJ5IGZvciB0aGUgY29uZnVzaW9uIGJ1dCBJIHNlbnQgdGhlIGFwcGxpY2F0aW9uIGV2ZW4gSSBwYWlkIA0KPj4-Pj4-Pj4-IDM1ICQNCj4-Pj4-Pj4-Pg0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4NCj4-Pj4-Pj4-PiBJIGF3YWl0IHlvdXIgcHJvbXB0IHJlcGx5DQo-Pj4-Pj4-Pj4NCj4-Pj4-Pj4-Pg0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gU2VudCBmcm9tIG15IGlQaG9uZQ0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4NCj4-Pj4-Pj4-Pg0KPj4-Pj4-Pj4-ID4gT24gRGVjIDgsIDIwMjAsIGF0IDc6MTggUE0sIEFwcGxpY2F0aW9uIFRlYW0gPA0KPj4-Pj4-Pj4-IGFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbT4gd3JvdGU6DQo-Pj4-Pj4-Pj4NCj4-Pj4-Pj4-PiA-IA0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gPiDvu78NCj4-Pj4-Pj4-Pg0KPj4-Pj4-Pj4-ID4gSGkgSmF2aWVyLA0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gPiANCj4-Pj4-Pj4-Pg0KPj4-Pj4-Pj4-ID4gSGF2ZW4ndCBoZWFyZCBmcm9tIHlvdSBpbiBhIGZldyBkYXlzIHNvIHJlYWNoaW5nIG91dCB0byBjb25maXJtIA0KPj4-Pj4-Pj4-IHlvdSdyZSBubyBsb25nZXIgaW50ZXJlc3RlZCBpbiBob3VzaW5nIGF0IFNKU1UuDQo-Pj4-Pj4-Pj4NCj4-Pj4-Pj4-PiA-IA0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gPiBCZXN0LA0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gPiBUeWxlcg0KPj4-Pj4-Pj4-DQo-Pj4-Pj4-Pj4gLS0gDQo-Pj4-Pj4-PiBCZXN0LA0KPj4-Pj4-Pj4NCj4-Pj4-Pj4-IFR5bGVyIEdhbGRlcw0KPj4-Pj4-Pj4gQ2xlYW4gRmxvb3JzICYgTG9ja2luZyBEb29ycw0KPj4-Pj4-Pj4NCj4-Pj4-Pj4-DQo='}, 'mimeType': 'text/plain', 'headers': [{'value': 'text/plain; charset="UTF-8"', 'name': 'Content-Type'}, {'value': 'quoted-printable', 'name': 'Content-Transfer-Encoding'}], 'partId': '0.0'}, {'filename': '', 'body': {'size': 10062, 'data': 'PGRpdiBkaXI9Imx0ciI-dGhpcyBpcyBhIGRyYWZ0IHVzZWQgZm9yIHRlc3RpbmcgcHVycG9zZXM8YnI-PGJyPjwvZGl2Pjxicj48ZGl2IGNsYXNzPSJnbWFpbF9xdW90ZSI-PGRpdiBkaXI9Imx0ciIgY2xhc3M9ImdtYWlsX2F0dHIiPk9uIEZyaSwgRGVjIDExLCAyMDIwIGF0IDc6NTMgUE0gSmF2aWVyIEZlcnJlciAmbHQ7PGEgaHJlZj0ibWFpbHRvOmphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tIj5qYXZpZXJmZXJyZXIwNjA2QGdtYWlsLmNvbTwvYT4mZ3Q7IHdyb3RlOjxicj48L2Rpdj48YmxvY2txdW90ZSBjbGFzcz0iZ21haWxfcXVvdGUiIHN0eWxlPSJtYXJnaW46MHB4IDBweCAwcHggMC44ZXg7Ym9yZGVyLWxlZnQ6MXB4IHNvbGlkIHJnYigyMDQsMjA0LDIwNCk7cGFkZGluZy1sZWZ0OjFleCI-PGRpdiBkaXI9ImF1dG8iPlRoYW5rIFXCoDwvZGl2PjxkaXY-PGJyPjxkaXYgY2xhc3M9ImdtYWlsX3F1b3RlIj48ZGl2IGRpcj0ibHRyIiBjbGFzcz0iZ21haWxfYXR0ciI-T24gRnJpLCBEZWMgMTEsIDIwMjAgYXQgNzo1MiBQTSBBcHBsaWNhdGlvbiBUZWFtICZsdDs8YSBocmVmPSJtYWlsdG86YXBwbHlAY2xlYW5mbG9vcnNsb2NraW5nZG9vcnMuY29tIiB0YXJnZXQ9Il9ibGFuayI-YXBwbHlAY2xlYW5mbG9vcnNsb2NraW5nZG9vcnMuY29tPC9hPiZndDsgd3JvdGU6PGJyPjwvZGl2PjxibG9ja3F1b3RlIGNsYXNzPSJnbWFpbF9xdW90ZSIgc3R5bGU9Im1hcmdpbjowcHggMHB4IDBweCAwLjhleDtib3JkZXItbGVmdDoxcHggc29saWQgcmdiKDIwNCwyMDQsMjA0KTtwYWRkaW5nLWxlZnQ6MWV4Ij48ZGl2IGRpcj0ibHRyIj5PayBzb3VuZHMgZ29vZCwgSSYjMzk7bGwgZm9yd2FyZCBpdCB0byB0aGUgcHJvcGVydHkgb3duZXJzLjxkaXY-PGJyIGNsZWFyPSJhbGwiPjxkaXY-PGRpdiBkaXI9Imx0ciI-PGRpdiBkaXI9Imx0ciI-QmVzdCw8ZGl2PlR5bGVyPC9kaXY-PGRpdj5DRiZhbXA7TEQ8L2Rpdj48L2Rpdj48L2Rpdj48L2Rpdj48YnI-PC9kaXY-PC9kaXY-PGJyPjxkaXYgY2xhc3M9ImdtYWlsX3F1b3RlIj48ZGl2IGRpcj0ibHRyIiBjbGFzcz0iZ21haWxfYXR0ciI-T24gRnJpLCBEZWMgMTEsIDIwMjAgYXQgNzoyNiBQTSBKYXZpZXIgRmVycmVyICZsdDs8YSBocmVmPSJtYWlsdG86amF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb20iIHRhcmdldD0iX2JsYW5rIj5qYXZpZXJmZXJyZXIwNjA2QGdtYWlsLmNvbTwvYT4mZ3Q7IHdyb3RlOjxicj48L2Rpdj48YmxvY2txdW90ZSBjbGFzcz0iZ21haWxfcXVvdGUiIHN0eWxlPSJtYXJnaW46MHB4IDBweCAwcHggMC44ZXg7Ym9yZGVyLWxlZnQ6MXB4IHNvbGlkIHJnYigyMDQsMjA0LDIwNCk7cGFkZGluZy1sZWZ0OjFleCI-PGRpdiBkaXI9ImF1dG8iPkkgd2FzIGNoZWNraW5nIG15IGNyZWRpdCBrYXJtYSBhbmQgaW4gZWZmZWN0IEkgaGF2ZSBteSBwcmV2aW91cyBhZGRyZXNzwqA8ZGl2PjxhIGhyZWY9Imh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vbWFwcy9zZWFyY2gvMjU1K3N3KzExdGgrc3QrYXB0KzQwMit6aXArMzMxMzArTWlhbWkrRmxvcmlkYT9lbnRyeT1nbWFpbCZhbXA7c291cmNlPWciIHRhcmdldD0iX2JsYW5rIj4yNTUgc3cgMTF0aCBzdCBhcHQgNDAyIHppcCAzMzEzMCBNaWFtaSBGbG9yaWRhPC9hPsKgPC9kaXY-PGRpdj48YnI-PC9kaXY-PGRpdj50aGVyZSBpcyBhIHByb2JsZW0gd2l0aCB0aGF0ID8_PGJyPjxicj48ZGl2IGRpcj0ibHRyIj5TZW50IGZyb20gbXkgaVBob25lPC9kaXY-PGRpdiBkaXI9Imx0ciI-PGJyPjxibG9ja3F1b3RlIHR5cGU9ImNpdGUiPk9uIERlYyAxMSwgMjAyMCwgYXQgMTE6NTEgQU0sIEphdmllciBGZXJyZXIgJmx0OzxhIGhyZWY9Im1haWx0bzpqYXZpZXJmZXJyZXIwNjA2QGdtYWlsLmNvbSIgdGFyZ2V0PSJfYmxhbmsiPmphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tPC9hPiZndDsgd3JvdGU6PGJyPjxicj48L2Jsb2NrcXVvdGU-PC9kaXY-PGJsb2NrcXVvdGUgdHlwZT0iY2l0ZSI-PGRpdiBkaXI9Imx0ciI-77u_WWVzIGl04oCZcyBteSBzc24gODgyIC0gNTEgLTQzMzfCoDxkaXY-PGJyPjwvZGl2PjxkaXY-TXkgc3NuIGhhcyBiZWVuIGZvciA0IHllYXJzLiBJIGRvbiYjMzk7dCB1bmRlcnN0YW5kIHRoZSBwcm9ibGVtLCBjb3VsZCB5b3UgZXhwbGFpbiBpdCB0byBtZT88L2Rpdj48ZGl2Pjxicj48L2Rpdj48ZGl2PmJlY2F1c2Ugb2YgdGhlIGNvdmlkIEkgaGFkIHByb2JsZW1zIHdpdGggbXkgY3JlZGl0IHNjb3JlIGJ1dCBJIGNhbiBzaG93IHlvdSBteSBhY2NvdW50IHN0YXRlbWVudHM8YnI-PGJyPjxkaXYgZGlyPSJsdHIiPlNlbnQgZnJvbSBteSBpUGhvbmU8L2Rpdj48ZGl2IGRpcj0ibHRyIj48YnI-PGJsb2NrcXVvdGUgdHlwZT0iY2l0ZSI-T24gRGVjIDExLCAyMDIwLCBhdCAxMTo0NCBBTSwgQXBwbGljYXRpb24gVGVhbSAmbHQ7PGEgaHJlZj0ibWFpbHRvOmFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbSIgdGFyZ2V0PSJfYmxhbmsiPmFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbTwvYT4mZ3Q7IHdyb3RlOjxicj48YnI-PC9ibG9ja3F1b3RlPjwvZGl2PjxibG9ja3F1b3RlIHR5cGU9ImNpdGUiPjxkaXYgZGlyPSJsdHIiPu-7vzxkaXYgZGlyPSJsdHIiPkhpIEphdmllciw8ZGl2Pjxicj48L2Rpdj48ZGl2PkJlZm9yZSBJIGRvLSBJIGhhdmUgdGhlIGZvbGxvd2luZyBub3RlIGluIHRoZSBjcmVkaXQgcmVwb3J0IGZyb20gVHJhbnN1bmlvbi48L2Rpdj48ZGl2Pjxicj48L2Rpdj48ZGl2PjxzcGFuIHN0eWxlPSJib3gtc2l6aW5nOmluaGVyaXQ7Zm9udC1zaXplOjE0cHg7bWFyZ2luOjBweDtib3JkZXI6MHB4O291dGxpbmU6MHB4O3BhZGRpbmc6MHB4O3ZlcnRpY2FsLWFsaWduOmJhc2VsaW5lO2xpbmUtaGVpZ2h0OjI1cHg7Zm9udC1mYW1pbHk6UHJveGltYU5vdmEsYXJpYWwsc2Fucy1zZXJpZjtjb2xvcjpyZ2IoMjUsMjUsMjUpO2JhY2tncm91bmQtcG9zaXRpb246MHB4IDBweCI-PHNwYW4gc3R5bGU9ImJveC1zaXppbmc6aW5oZXJpdDttYXJnaW46MHB4O2JvcmRlcjowcHg7b3V0bGluZTowcHg7cGFkZGluZzowcHg7dmVydGljYWwtYWxpZ246YmFzZWxpbmU7ZGlzcGxheTpibG9jaztsaW5lLWhlaWdodDoyNXB4O2ZvbnQtZmFtaWx5OlByb3hpbWFOb3ZhLGFyaWFsLHNhbnMtc2VyaWY7YmFja2dyb3VuZC1wb3NpdGlvbjowcHggMHB4Ij5DdXJyZW50IGFkZHJlc3MgbWlzbWF0Y2ggLSBpbnB1dCBkb2VzIG5vdCBtYXRjaCBmaWxlLjwvc3Bhbj48L3NwYW4-PHNwYW4gc3R5bGU9ImJveC1zaXppbmc6aW5oZXJpdDtmb250LXNpemU6MTRweDttYXJnaW46MHB4O2JvcmRlcjowcHg7b3V0bGluZTowcHg7cGFkZGluZzowcHg7dmVydGljYWwtYWxpZ246YmFzZWxpbmU7bGluZS1oZWlnaHQ6MjVweDtmb250LWZhbWlseTpQcm94aW1hTm92YSxhcmlhbCxzYW5zLXNlcmlmO2NvbG9yOnJnYigyNSwyNSwyNSk7YmFja2dyb3VuZC1wb3NpdGlvbjowcHggMHB4Ij48c3BhbiBzdHlsZT0iYm94LXNpemluZzppbmhlcml0O21hcmdpbjowcHg7Ym9yZGVyOjBweDtvdXRsaW5lOjBweDtwYWRkaW5nOjBweDt2ZXJ0aWNhbC1hbGlnbjpiYXNlbGluZTtkaXNwbGF5OmJsb2NrO2xpbmUtaGVpZ2h0OjI1cHg7Zm9udC1mYW1pbHk6UHJveGltYU5vdmEsYXJpYWwsc2Fucy1zZXJpZjtiYWNrZ3JvdW5kLXBvc2l0aW9uOjBweCAwcHgiPlNTTiBtYXkgYmUgaW52YWxpZCAtIGl0IHdhcyBlaXRoZXIgdmVyeSByZWNlbnRseSBvciBuZXZlciBpc3N1ZWQgYnkgdGhlIFNvY2lhbCBTZWN1cml0eSBBZG1pbmlzdHJhdGlvbi48L3NwYW4-PHNwYW4gc3R5bGU9ImJveC1zaXppbmc6aW5oZXJpdDttYXJnaW46MHB4O2JvcmRlcjowcHg7b3V0bGluZTowcHg7cGFkZGluZzowcHg7dmVydGljYWwtYWxpZ246YmFzZWxpbmU7ZGlzcGxheTpibG9jaztsaW5lLWhlaWdodDoyNXB4O2ZvbnQtZmFtaWx5OlByb3hpbWFOb3ZhLGFyaWFsLHNhbnMtc2VyaWY7YmFja2dyb3VuZC1wb3NpdGlvbjowcHggMHB4Ij48YnI-PC9zcGFuPjxzcGFuIHN0eWxlPSJib3gtc2l6aW5nOmluaGVyaXQ7bWFyZ2luOjBweDtib3JkZXI6MHB4O291dGxpbmU6MHB4O3BhZGRpbmc6MHB4O3ZlcnRpY2FsLWFsaWduOmJhc2VsaW5lO2Rpc3BsYXk6YmxvY2s7bGluZS1oZWlnaHQ6MjVweDtmb250LWZhbWlseTpQcm94aW1hTm92YSxhcmlhbCxzYW5zLXNlcmlmO2JhY2tncm91bmQtcG9zaXRpb246MHB4IDBweCI-Q2FuIHlvdSBjb25maXJtIHRoYXQgdGhlIHNvY2lhbCB5b3UgZW50ZXJlZCB3YXMgY29ycmVjdD8gSWYgaXQgd2FzIHJlY2VudGx5wqBpc3N1ZWQgY291bGQgeW91IGV4cGxhaW4gd2h5IGFuZCBzdWJtaXQgc3VwcG9ydGluZ8KgZG9jdW1lbnRhdGlvbj8gQXMgaXQgc3RhbmRzIHJpZ2h0IG5vdyBiYXNlZCBvbiB0aGUgc29jaWFsIG51bWJlciBhbmQgdGhlIG51bWJlciBvZiBjb2xsZWN0aW9ucyB5b3UmIzM5O3ZlIGhhZCByZWNlbnRseSBJIHdvdWxkIHJlY29tbWVuZMKgdG8gdGhlIG93bmVycyB0aGF0IHRoZXkgZG8gbm90IGFwcHJvdmUgeW91ciBhcHBsaWNhdGlvbi48L3NwYW4-PHNwYW4gc3R5bGU9ImJveC1zaXppbmc6aW5oZXJpdDttYXJnaW46MHB4O2JvcmRlcjowcHg7b3V0bGluZTowcHg7cGFkZGluZzowcHg7dmVydGljYWwtYWxpZ246YmFzZWxpbmU7ZGlzcGxheTpibG9jaztsaW5lLWhlaWdodDoyNXB4O2ZvbnQtZmFtaWx5OlByb3hpbWFOb3ZhLGFyaWFsLHNhbnMtc2VyaWY7YmFja2dyb3VuZC1wb3NpdGlvbjowcHggMHB4Ij48YnI-PC9zcGFuPjwvc3Bhbj48ZGl2PjxkaXYgZGlyPSJsdHIiPjxkaXYgZGlyPSJsdHIiPkJlc3QsPGRpdj5UeWxlcjwvZGl2PjxkaXY-Q0YmYW1wO0xEPC9kaXY-PC9kaXY-PC9kaXY-PC9kaXY-PGJyPjwvZGl2PjwvZGl2Pjxicj48ZGl2IGNsYXNzPSJnbWFpbF9xdW90ZSI-PGRpdiBkaXI9Imx0ciIgY2xhc3M9ImdtYWlsX2F0dHIiPk9uIEZyaSwgRGVjIDExLCAyMDIwIGF0IDExOjM4IEFNIEFwcGxpY2F0aW9uIFRlYW0gJmx0OzxhIGhyZWY9Im1haWx0bzphcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb20iIHRhcmdldD0iX2JsYW5rIj5hcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb208L2E-Jmd0OyB3cm90ZTo8YnI-PC9kaXY-PGJsb2NrcXVvdGUgY2xhc3M9ImdtYWlsX3F1b3RlIiBzdHlsZT0ibWFyZ2luOjBweCAwcHggMHB4IDAuOGV4O2JvcmRlci1sZWZ0OjFweCBzb2xpZCByZ2IoMjA0LDIwNCwyMDQpO3BhZGRpbmctbGVmdDoxZXgiPjxkaXYgZGlyPSJsdHIiPk9rIGdyZWF0LiBJJiMzOTt2ZSBmb3J3YXJkZWQgdGhlIHJlcG9ydHMgdG8gdGhlIG93bmVycyBmb3IgYXBwcm92YWwuPGRpdj48YnIgY2xlYXI9ImFsbCI-PGRpdj48ZGl2IGRpcj0ibHRyIj48ZGl2IGRpcj0ibHRyIj5CZXN0LDxkaXY-VHlsZXI8L2Rpdj48ZGl2PkNGJmFtcDtMRDwvZGl2PjwvZGl2PjwvZGl2PjwvZGl2Pjxicj48L2Rpdj48L2Rpdj48YnI-PGRpdiBjbGFzcz0iZ21haWxfcXVvdGUiPjxkaXYgZGlyPSJsdHIiIGNsYXNzPSJnbWFpbF9hdHRyIj5PbiBXZWQsIERlYyA5LCAyMDIwIGF0IDEwOjQyIFBNIEphdmllciBGZXJyZXIgJmx0OzxhIGhyZWY9Im1haWx0bzpqYXZpZXJmZXJyZXIwNjA2QGdtYWlsLmNvbSIgdGFyZ2V0PSJfYmxhbmsiPmphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tPC9hPiZndDsgd3JvdGU6PGJyPjwvZGl2PjxibG9ja3F1b3RlIGNsYXNzPSJnbWFpbF9xdW90ZSIgc3R5bGU9Im1hcmdpbjowcHggMHB4IDBweCAwLjhleDtib3JkZXItbGVmdDoxcHggc29saWQgcmdiKDIwNCwyMDQsMjA0KTtwYWRkaW5nLWxlZnQ6MWV4Ij48ZGl2IGRpcj0iYXV0byI-SSBoYWQgYSB0aWNrZXQgYmVjYXVzZSBvZiB0aGUgc2VhdGJlbHQgYnV0IHRoZSBqdWRnZSBkaXNtaXNzZWQgdGhlIGNhc2UgLnRoZSBzZWNvbmQgb25lIGRlZmluaXRlbHkgd2FzbuKAmXQgbWU8YnI-PGJyPjxkaXYgZGlyPSJsdHIiPlNlbnQgZnJvbSBteSBpUGhvbmU8L2Rpdj48ZGl2IGRpcj0ibHRyIj48YnI-PGJsb2NrcXVvdGUgdHlwZT0iY2l0ZSI-T24gRGVjIDksIDIwMjAsIGF0IDc6MjEgUE0sIEFwcGxpY2F0aW9uIFRlYW0gJmx0OzxhIGhyZWY9Im1haWx0bzphcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb20iIHRhcmdldD0iX2JsYW5rIj5hcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb208L2E-Jmd0OyB3cm90ZTo8YnI-PGJyPjwvYmxvY2txdW90ZT48L2Rpdj48YmxvY2txdW90ZSB0eXBlPSJjaXRlIj48ZGl2IGRpcj0ibHRyIj7vu788ZGl2IGRpcj0ibHRyIj5IaSBKYXZpZXIsPGRpdj48YnI-PC9kaXY-PGRpdj5JbiB5b3VyIGFwcGxpY2F0aW9uIEkgc2VlIHR3byBjcmltaW5hbCByZXBvcnRzIGluIG1pYW1pLCBvbmUgcmVsYXRlZCB0byBkcml2aW5nIHdpdGhvdXQgYSBzZWF0YmVsdCwgb25lIGZvciB0cmVzcGFzc2luZy4gSSBkb24mIzM5O3QgdGhpbmsgZWl0aGVyIG9mIHRob3NlIHdpbGwgYmUgZGVhbGJyZWFrZXJzIGZvciB0aGUgb3duZXJzLCBidXQgSSYjMzk7bSByZWFjaGluZyBvdXQgdG8gYXNrIGlmIHRoZXkgd2VyZSB5b3UuIFRoZSBsYXN0IG5hbWVzIG9uIGJvdGggYXJlIGRpZmZlcmVudCB0aGFuIHlvdXJzLCBidXQgdGhlIGZpcnN0IGFuZCBtaWRkbGUgbmFtZXMgbWF0Y2guPC9kaXY-PGRpdj48YnIgY2xlYXI9ImFsbCI-PGRpdj48ZGl2IGRpcj0ibHRyIj48ZGl2IGRpcj0ibHRyIj5CZXN0LDxkaXY-VHlsZXI8L2Rpdj48ZGl2PkNGJmFtcDtMRDwvZGl2PjwvZGl2PjwvZGl2PjwvZGl2Pjxicj48L2Rpdj48L2Rpdj48YnI-PGRpdiBjbGFzcz0iZ21haWxfcXVvdGUiPjxkaXYgZGlyPSJsdHIiIGNsYXNzPSJnbWFpbF9hdHRyIj5PbiBXZWQsIERlYyA5LCAyMDIwIGF0IDQ6MzUgUE0gSmF2aWVyIEZlcnJlciAmbHQ7PGEgaHJlZj0ibWFpbHRvOmphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tIiB0YXJnZXQ9Il9ibGFuayI-amF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb208L2E-Jmd0OyB3cm90ZTo8YnI-PC9kaXY-PGJsb2NrcXVvdGUgY2xhc3M9ImdtYWlsX3F1b3RlIiBzdHlsZT0ibWFyZ2luOjBweCAwcHggMHB4IDAuOGV4O2JvcmRlci1sZWZ0OjFweCBzb2xpZCByZ2IoMjA0LDIwNCwyMDQpO3BhZGRpbmctbGVmdDoxZXgiPjxkaXYgZGlyPSJhdXRvIj5JIGp1c3QgZm91bmRlZCB0aGUgZW1haWwgYW5kIGZpbmlzaGVkIHRoZSB0cmFuc1VuaW9uIGFwcGxpY2F0aW9uwqA8L2Rpdj48ZGl2IGRpcj0iYXV0byI-PGJyPjwvZGl2PjxkaXY-PGJyPjxkaXYgY2xhc3M9ImdtYWlsX3F1b3RlIj48ZGl2IGRpcj0ibHRyIiBjbGFzcz0iZ21haWxfYXR0ciI-T24gV2VkLCBEZWMgOSwgMjAyMCBhdCA0OjE5IFBNIEFwcGxpY2F0aW9uIFRlYW0gJmx0OzxhIGhyZWY9Im1haWx0bzphcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb20iIHRhcmdldD0iX2JsYW5rIj5hcHBseUBjbGVhbmZsb29yc2xvY2tpbmdkb29ycy5jb208L2E-Jmd0OyB3cm90ZTo8YnI-PC9kaXY-PGJsb2NrcXVvdGUgY2xhc3M9ImdtYWlsX3F1b3RlIiBzdHlsZT0ibWFyZ2luOjBweCAwcHggMHB4IDAuOGV4O2JvcmRlci1sZWZ0OjFweCBzb2xpZCByZ2IoMjA0LDIwNCwyMDQpO3BhZGRpbmctbGVmdDoxZXgiPjxkaXYgZGlyPSJsdHIiPkhpIEphdmllciw8ZGl2Pjxicj48L2Rpdj48ZGl2PlRoZSBpbmZvIEkgaGF2ZSBzYXlzIGl0JiMzOTtzIGJlZW4gc2VudC4gUGxlYXNlIGNoZWNrIHlvdSBzcGFtIGZvbGRlci48L2Rpdj48ZGl2PjxiciBjbGVhcj0iYWxsIj48ZGl2PjxkaXYgZGlyPSJsdHIiPjxkaXYgZGlyPSJsdHIiPkJlc3QsPGRpdj5UeWxlcjwvZGl2PjxkaXY-Q0YmYW1wO0xEPC9kaXY-PC9kaXY-PC9kaXY-PC9kaXY-PGJyPjwvZGl2PjwvZGl2Pjxicj48ZGl2IGNsYXNzPSJnbWFpbF9xdW90ZSI-PGRpdiBkaXI9Imx0ciIgY2xhc3M9ImdtYWlsX2F0dHIiPk9uIFdlZCwgRGVjIDksIDIwMjAgYXQgMTA6MTUgQU0gSmF2aWVyIEZlcnJlciAmbHQ7PGEgaHJlZj0ibWFpbHRvOmphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tIiB0YXJnZXQ9Il9ibGFuayI-amF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb208L2E-Jmd0OyB3cm90ZTo8YnI-PC9kaXY-PGJsb2NrcXVvdGUgY2xhc3M9ImdtYWlsX3F1b3RlIiBzdHlsZT0ibWFyZ2luOjBweCAwcHggMHB4IDAuOGV4O2JvcmRlci1sZWZ0OjFweCBzb2xpZCByZ2IoMjA0LDIwNCwyMDQpO3BhZGRpbmctbGVmdDoxZXgiPjxkaXYgZGlyPSJhdXRvIj5J4oCZbSBzb3JyeSBidXQsIEkgZG9u4oCZdCBoYXZlIGFueSBlbWFpbCBmcm9tIHRyYW5zVW5pb24uwqA8YnI-PGJyPjxkaXYgZGlyPSJsdHIiPlNlbnQgZnJvbSBteSBpUGhvbmU8L2Rpdj48ZGl2IGRpcj0ibHRyIj48YnI-PGJsb2NrcXVvdGUgdHlwZT0iY2l0ZSI-T24gRGVjIDksIDIwMjAsIGF0IDEwOjA4IEFNLCBBcHBsaWNhdGlvbiBUZWFtICZsdDs8YSBocmVmPSJtYWlsdG86YXBwbHlAY2xlYW5mbG9vcnNsb2NraW5nZG9vcnMuY29tIiB0YXJnZXQ9Il9ibGFuayI-YXBwbHlAY2xlYW5mbG9vcnNsb2NraW5nZG9vcnMuY29tPC9hPiZndDsgd3JvdGU6PGJyPjxicj48L2Jsb2NrcXVvdGU-PC9kaXY-PGJsb2NrcXVvdGUgdHlwZT0iY2l0ZSI-PGRpdiBkaXI9Imx0ciI-77u_PGRpdiBkaXI9ImF1dG8iPkhpIEphdmllciw8L2Rpdj48ZGl2IGRpcj0iYXV0byI-PGJyPjwvZGl2PjxkaXYgZGlyPSJhdXRvIj5QbGVhc2UgbG9vayBmb3IgYW4gZW1haWwgZnJvbSBUcmFuc3VuaW9uLjwvZGl2PjxkaXYgZGlyPSJhdXRvIj48YnI-PC9kaXY-PGRpdiBkaXI9ImF1dG8iPlR5bGVyPC9kaXY-PGRpdj48YnI-PGRpdiBjbGFzcz0iZ21haWxfcXVvdGUiPjxkaXYgZGlyPSJsdHIiIGNsYXNzPSJnbWFpbF9hdHRyIj5PbiBUdWUsIERlYyA4LCAyMDIwIGF0IDY6MDYgUE0gSmF2aWVyIEZlcnJlciAmbHQ7PGEgaHJlZj0ibWFpbHRvOmphdmllcmZlcnJlcjA2MDZAZ21haWwuY29tIiB0YXJnZXQ9Il9ibGFuayI-amF2aWVyZmVycmVyMDYwNkBnbWFpbC5jb208L2E-Jmd0OyB3cm90ZTo8YnI-PC9kaXY-PGJsb2NrcXVvdGUgY2xhc3M9ImdtYWlsX3F1b3RlIiBzdHlsZT0ibWFyZ2luOjBweCAwcHggMHB4IDAuOGV4O2JvcmRlci1sZWZ0OjFweCBzb2xpZCByZ2IoMjA0LDIwNCwyMDQpO3BhZGRpbmctbGVmdDoxZXgiPkkmIzM5O20gc29ycnkgZm9yIHRoZSBjb25mdXNpb24gYnV0IEkgc2VudCB0aGUgYXBwbGljYXRpb24gZXZlbiBJIHBhaWQgMzUgJDxicj48YnI-PGJyPjxicj5JIGF3YWl0IHlvdXIgcHJvbXB0IHJlcGx5PGJyPjxicj48YnI-PGJyPlNlbnQgZnJvbSBteSBpUGhvbmU8YnI-PGJyPjxicj48YnI-Jmd0OyBPbiBEZWMgOCwgMjAyMCwgYXQgNzoxOCBQTSwgQXBwbGljYXRpb24gVGVhbSAmbHQ7PGEgaHJlZj0ibWFpbHRvOmFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbSIgdGFyZ2V0PSJfYmxhbmsiPmFwcGx5QGNsZWFuZmxvb3JzbG9ja2luZ2Rvb3JzLmNvbTwvYT4mZ3Q7IHdyb3RlOjxicj48YnI-Jmd0OyA8YnI-PGJyPiZndDsg77u_PGJyPjxicj4mZ3Q7IEhpIEphdmllciw8YnI-PGJyPiZndDsgPGJyPjxicj4mZ3Q7IEhhdmVuJiMzOTt0IGhlYXJkIGZyb20geW91IGluIGEgZmV3IGRheXMgc28gcmVhY2hpbmcgb3V0IHRvIGNvbmZpcm0geW91JiMzOTtyZSBubyBsb25nZXIgaW50ZXJlc3RlZCBpbiBob3VzaW5nIGF0IFNKU1UuPGJyPjxicj4mZ3Q7IDxicj48YnI-Jmd0OyBCZXN0LDxicj48YnI-Jmd0OyBUeWxlcjxicj48YnI-PC9ibG9ja3F1b3RlPjwvZGl2PjwvZGl2Pi0tIDxicj48ZGl2IGRpcj0ibHRyIj5CZXN0LDxicj48YnI-VHlsZXIgR2FsZGVzPGJyPkNsZWFuIEZsb29ycyAmYW1wOyBMb2NraW5nIERvb3JzPC9kaXY-DQo8L2Rpdj48L2Jsb2NrcXVvdGU-PC9kaXY-PC9ibG9ja3F1b3RlPjwvZGl2Pg0KPC9ibG9ja3F1b3RlPjwvZGl2PjwvZGl2Pg0KPC9ibG9ja3F1b3RlPjwvZGl2Pg0KPC9kaXY-PC9ibG9ja3F1b3RlPjwvZGl2PjwvYmxvY2txdW90ZT48L2Rpdj4NCjwvYmxvY2txdW90ZT48L2Rpdj4NCjwvZGl2PjwvYmxvY2txdW90ZT48L2Rpdj48L2Rpdj48L2Jsb2NrcXVvdGU-PC9kaXY-PC9kaXY-PC9ibG9ja3F1b3RlPjwvZGl2Pg0KPC9ibG9ja3F1b3RlPjwvZGl2PjwvZGl2Pg0KPC9ibG9ja3F1b3RlPjwvZGl2Pg0K'}, 'mimeType': 'text/html', 'headers': [{'value': 'text/html; charset="UTF-8"', 'name': 'Content-Type'}, {'value': 'quoted-printable', 'name': 'Content-Transfer-Encoding'}], 'partId': '0.1'}], 'mimeType': 'multipart/alternative', 'headers': [{'value': 'multipart/alternative; boundary="000000000000d8c81605b64bd332"', 'name': 'Content-Type'}], 'partId': '0', 'filename': '', 'body': {'size': 0}}, {'filename': 'deleteme.pdf', 'body': {'size': 789, 'attachmentId': 'ANGjdJ8ivHen0PYjVS-VRle2sfVeMQQpq2aDVy2LA5LKOPnUFl4gyeMIh7ZPQLzxghh1oL1zIkcUP5YO32ua7og8bCpu1RMBm4DEshHmZfUJqILLuYRHj9v6_qbPfm34j2zkZ_52mijJKde3_8Pt4cBeWc3hLRUkstq3kcHVm2z76YLxAAYejCfXS7k_3Y-MdVdVmZOb_BRqN_UaMSqrn3dzucLkVTI2Lku2dfmyCA'}, 'mimeType': 'application/pdf', 'headers': [{'value': 'application/pdf; name="deleteme.pdf"', 'name': 'Content-Type'}, {'value': 'attachment; filename="deleteme.pdf"', 'name': 'Content-Disposition'}, {'value': 'base64', 'name': 'Content-Transfer-Encoding'}, {'value': 'f_kim9jqqz0', 'name': 'X-Attachment-Id'}, {'value': '<f_kim9jqqz0>', 'name': 'Content-ID'}], 'partId': '1'}], 'mimeType': 'multipart/mixed', 'headers': [{'value': '1.0', 'name': 'MIME-Version'}, {'value': 'Sat, 12 Dec 2020 17:21:15 -0500', 'name': 'Date'}, {'value': '<96745E44-1CDD-40B2-9396-262B1B3BCC06@gmail.com> <0B1F57E3-401C-48C2-99C3-BF9D91E524E6@gmail.com> <CAAD9TVVZjveeBfVC5+AxTLcyi6CxHvum-bk0X-d6MhrGF3fUng@mail.gmail.com> <CA+twOtbjEO=i8Z5476fykqjUVu6z9o8w-3j1Dwhs6p+3NDJ8rA@mail.gmail.com>', 'name': 'References'}, {'value': '<CA+twOtbjEO=i8Z5476fykqjUVu6z9o8w-3j1Dwhs6p+3NDJ8rA@mail.gmail.com>', 'name': 'In-Reply-To'}, {'value': '<CAAD9TVV6PT6guZNgmrA8JS-88bQ=+=U_OrJnfAeiN6nVou0j2A@mail.gmail.com>', 'name': 'Message-ID'}, {'value': 'Re: New submission for SJSU', 'name': 'Subject'}, {'value': 'Application Team <apply@cleanfloorslockingdoors.com>', 'name': 'From'}, {'value': 'Javier Ferrer <pulkitagarwalcs@gmail.com>', 'name': 'To'}, {'value': 'multipart/mixed; boundary="000000000000d8c81905b64bd334"', 'name': 'Content-Type'}], 'partId': '', 'filename': '', 'body': {'size': 0}}, 'snippet': 'this is a draft used for testing purposes On Fri, Dec 11, 2020 at 7:53 PM Javier Ferrer &lt;javierferrer0606@gmail.com&gt; wrote: Thank U On Fri, Dec 11, 2020 at 7:52 PM Application Team &lt;apply@', 'internalDate': '1607811675000', 'historyId': '1478071', 'labelIds': ['DRAFT'], 'id': draft_msg_id}, mock_service))
        mock_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        mock_service.get_user = MagicMock(return_value='apply')
        mock_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        attachment_data = 'abcdefghijklmnop'
        mock_service.get_attachment = MagicMock(return_value={'data' : 'YWJjZGVmZ2hpamtsbW5vcA==\n'})

        attachment_fn = 'test attachment.pdf'
        # add an attachment
        thread.add_attachment_to_draft(attachment_data, attachment_fn, thread.default_reply())
        # expected payload we pass to GMail service is harcoded here
        # do the asserts
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('pulkitagarwalcs@gmail.com', mime_multipart['to'])
        self.assertEqual('New submission for SJSU', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['References'])
        #self.assertEqual(existing_text, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])
        # This weird string is the base64 encoded version of our attachment_data
        self.assertEqual('YWJjZGVmZ2hpamtsbW5vcA==\n', mime_multipart.__dict__['_payload'][1].__dict__['_payload'])

        # Now we'll add an additional attachment
        attachment_data = 'abcdefghijklmnop'
        attachment_fn = 'test second attachment.pdf'
        # add an attachment
        thread.add_attachment_to_draft(attachment_data, attachment_fn, thread.default_reply())
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertEqual(thread.identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('pulkitagarwalcs@gmail.com', mime_multipart['to'])
        self.assertEqual('New submission for SJSU', mime_multipart['subject'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CAAD9TVVj3xy5=oH0CpNozRUu-zKWLvQKyzBPQgE9+6nZJ1L-ZA@mail.gmail.com>', mime_multipart['References'])
        #self.assertEqual(existing_text, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])
        # We don't do the assert on the old attachment again because it would require getting a pdf that actually had data
        #self.assertEqual('YWJjZGVmZ2hpamtsbW5vcA==\n', mime_multipart.__dict__['_payload'][1].__dict__['_payload'])
        # Do the assert on the new attachment
        self.assertEqual('YWJjZGVmZ2hpamtsbW5vcA==\n', mime_multipart.__dict__['_payload'][2].__dict__['_payload'])
        
    def test_remove_existing_draft(self):
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_email_thread.txt'), mock_service)

        # With no draft, we shouldn't do anything on the service
        thread.remove_existing_draft()

        # Now we'll get a thread that has an existing draft
        mock_service = Mock()
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        mock_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        mock_service.delete_draft = MagicMock()

        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        thread.remove_existing_draft()
        mock_service.delete_draft.assert_called_once_with(draft_id)
        self.assertFalse(thread.has_draft())

    def test_age_in_days(self):
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        zero_ts = 1604096012000
        self.assertEqual(0, thread.age_in_days(now_f=lambda: thread.last_ts()))
        self.assertEqual(1, thread.age_in_days(now_f=lambda: thread.last_ts() + 86400))
        self.assertEqual(2, thread.age_in_days(now_f=lambda: thread.last_ts() + 86400 * 2))
        self.assertEqual(2, thread.age_in_days(now_f=lambda: thread.last_ts() + 86400 * 2 + 20))


    def test_len(self):
        # With a draft
        mock_service = Mock()
        mock_service.get_drafts = MagicMock(return_value=[{'id' : '5678', 'message' : {'id' : '2345'}}])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/message_from_tenant_then_message_and_draft_from_us.txt'), mock_service)
        self.assertEqual(2, len(thread))

        # Without a draft
        mock_service = Mock()
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_message_with_reply_to.txt'), mock_service)
        self.assertEqual(1, len(thread))

    # if we call append to draft multiple times with different recipients in each
    # call, we'll add all the recipients together for the draft we create
    def test_add_to_list_of_draft_recipients(self):
        mock_service = Mock()
        mock_service.get_drafts = MagicMock(return_value=[{'id' : '5678', 'message' : {'id' : '2345'}}])
        thread = Thread(*get_thread_constructor_args('thread_test_inputs/one_email_thread.txt'), mock_service)
        first_msg = 'draft line one'
        second_msg = 'draft line two'
        draft_id = '1234'
        draft_msg_id = '2345'
        email_one, email_two, email_three = 'email@one.com', 'email@two.com', 'email@three.com'
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg)}, 'headers' : [{'name' : 'to', 'value' : 'Bob bob <{}>'.format(email_one)}]}}, {}))
        thread.append_to_draft(first_msg, [email_one])
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg)}, 'headers' : [{'name' : 'to', 'value' : ' <{}>,<{}>'.format(email_one, email_two)}]}}, {}))
        thread.append_to_draft(second_msg, [email_two])
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]
        self.assertTrue(email_one in mime_multipart['to'])
        self.assertTrue(email_two in mime_multipart['to'])
        self.assertTrue(email_one in thread.messages[-1].recipients())
        self.assertTrue(email_two in thread.messages[-1].recipients())

        # now add a third recipient via the add attachement call
        mock_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : first_msg, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(first_msg)}, 'headers' : [{'name' : 'to', 'value' : ' <{}>,<{}>,<{}>'.format(email_one, email_two, email_three)}]}}, {}))

        attachment_data = 'abcdefghijklmnop'
        attachment_fn = 'test second attachment.pdf'
        # add an attachment
        thread.add_attachment_to_draft(attachment_data, attachment_fn, [email_three])
        mime_multipart, thread_id, called_draft_id = mock_service.append_or_create_draft.call_args[0]

        self.assertTrue(email_one in mime_multipart['to'])
        self.assertTrue(email_two in mime_multipart['to'])
        self.assertTrue(email_three in mime_multipart['to'])
        self.assertTrue(email_one in thread.messages[-1].recipients())
        self.assertTrue(email_two in thread.messages[-1].recipients())
        self.assertTrue(email_three in thread.messages[-1].recipients())

