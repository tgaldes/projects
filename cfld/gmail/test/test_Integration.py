from unittest.mock import MagicMock, Mock
import unittest

from framework.main import Main
from framework.Thread import Thread
from framework.Logger import Logger
from services.gmail.GMailMessage import GMailMessage

from test.TestUtil import get_thread_constructor_args, encode_for_payload
import test.TestConfig

class IntegrationTest(unittest.TestCase):

    def test_dummy(self):
        from orgs.example_org.ExampleOrg import signature
        #sheet_service = Mock()
        #sheet_service.get_rule_construction_data = MagicMock(return_value=[['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group', 'group_type', 'rule_type'], ['Label by school', 'apply', '', '', 'New submission for ([A-Za-z]*)', '', '', 'label', '"Schools/" + match(0)', '', '', '1', 'ifelse'], ['Label by school', 'apply', '', '', 'Zumper tenant lead for (.*) -.*', '', '', 'label', '"Schools/" + short_name(match(0))', '', '', '1', 'ifelse'], ['Label by school', 'apply', '', '', '[\\S^]* is requesting information about (.*?)[#,]', '', '', 'label', '"Schools/" + short_name(match(0))', '', '', '1', 'ifelse'], ['Label by school', 'apply', '', '', 'RentPath Lead from .* \\((.*)\\)', '', '', 'label', '"Schools/" + short_name(match(0))', '', '', '1', 'ifelse'], ['Label by school', 'apply', '', '', '[\\S^]* wants to tour (.*) -', '', '', 'label', '"Schools/" + short_name(match(0))', '', '', '1', 'ifelse'], ['Label by school', 'apply', '', '', '[\\S^]* is requesting an application for (.*) #.*', '', '', 'label', '"Schools/" + short_name(match(0))', '', '', '1', 'ifelse'], ['Remove catch all', 'apply', '', 'Schools/.*', '', '', '', 'unlabel', '"Catch all"', '', '', '1', 'ifelse'], ['Add catch all', 'apply', '', '', '.*', '', '', 'label', '"Catch all"', '', '', '1', 'ifelse'], [], ['Label 3rd party advertiser', 'apply', '', '', 'Zumper tenant lead for (.*) -.*', '', '', 'label', '"3rd_party"', '', '', '2', 'ifelse'], ['Label 3rd party advertiser', 'apply', '', '', '[\\S^]* is requesting information about (.*?)[#,]', '', '', 'label', '"3rd_party"', '', '', '2', 'ifelse'], ['Label 3rd party advertiser', 'apply', '', '', 'RentPath Lead from .* \\((.*)\\)', '', '', 'label', '"3rd_party"', '', '', '2', 'ifelse'], ['Label 3rd party advertiser', 'apply', '', '', '[\\S^]* wants to tour (.*) -', '', '', 'label', '"3rd_party"', '', '', '2', 'ifelse'], ['Label 3rd party advertiser', 'apply', '', '', '[\\S^]* is requesting an application for (.*) #.*', '', '', 'label', '"3rd_party"', '', '', '2', 'ifelse'], [], ['Remove existing draft', 'apply', '', 'automation', '', '', 'thread.has_existing_draft()', 'remove_draft', '', '', '', '3'], [], ['make them say no', 'apply', '', 'Schools/(.*)', '', '', 'thread.need_make_them_say_no()', 'draft', '"Haven\'t heard from you in a few days so reaching out to confirm you\'re no longer interested in housing at {}.<br><br>".format(match(0))', '', 'thread.default_reply()', '4'], [], ['general info match', 'apply', '', '3rd_party', '.*RentPath Lead.*', '.*additional details.*', 'not thread.is_last_message_from_us() and len(thread) == 1', 'empty', '', '', '', '5', 'ifany', 'if'], ['general info match', 'apply', '', '3rd_party', '', '.*learn.*', 'not thread.is_last_message_from_us() and len(thread) == 1', 'empty', '', '', '', '5', '', 'if'], \
        #['general info match', 'apply', '', '3rd_party', '', '.*more.*', 'not thread.is_last_message_from_us() and len(thread) == 1', 'empty', '', '', '', '5', '', 'if'], ['general info match', 'apply', '', '3rd_party', '', '.*information.*', 'not thread.is_last_message_from_us() and len(thread) == 1', 'empty', '', '', '', '5', '', 'if'], ['general info match', 'apply', '', '3rd_party', '', '.*interested.*', 'not thread.is_last_message_from_us() and len(thread) == 1', 'empty', '', '', '', '5', '', 'if'], ['general info match', 'apply', '', 'Schools/(.*)', '', '', '', 'draft', '"Thanks for reaching out! There\'s always up to date information for {} on our website cf-ld.com/{} and {}. Happy to answer any specific questions you have for me :)<br><br>".format(match(0), match(0).lower().replace(\' \', \'-\'), link("cf-ld.com/{}-faqs".format(match(0).lower().replace(\' \', \'-\'), "here")))', '', 'thread.default_reply()', '5', '', 'any'], [], ['3rd party requesting viewing', 'apply', '', 'Schools/(.*)', '', '.*schedule.*', 'not thread.is_last_message_from_us()', 'draft', '"Before we put you in touch with our on site manager for a viewing, we\'ll need you to fill out cf-ld.com/contact-form so we know a few basics about your desired stay at {}.<br><br>".format(match(0))', '', 'thread.default_reply()', '6', 'ifelse'], ['3rd party requesting viewing', 'apply', '', 'Schools/(.*)', '', '.*view.*', 'not thread.is_last_message_from_us()', 'draft', '"Before we put you in touch with our on site manager for a viewing, we\'ll need you to fill out cf-ld.com/contact-form so we know a few basics about your desired stay at {}.<br><br>".format(match(0))', '', 'thread.default_reply()', '6', 'ifelse'], ['3rd party requesting viewing', 'apply', '', 'Schools/(.*)', '', '.*tour.*', 'not thread.is_last_message_from_us()', 'draft', '"Before we put you in touch with our on site manager for a viewing, we\'ll need you to fill out cf-ld.com/contact-form so we know a few basics about your desired stay at {}.<br><br>".format(match(0))', '', 'thread.default_reply()', '6', 'ifelse'], [], ['available', 'apply', '', 'Schools/(.*)', '', '.*available.*', 'not thread.is_last_message_from_us()', 'empty', '', '', '', '7', 'ifany', 'if'], ['available', 'apply', '', 'Schools/(.*)', '', '.*availability.*', 'not thread.is_last_message_from_us()', 'empty', '', '', '', '7', '', 'if'], ['available', 'apply', '', 'Schools/(.*)', '', '', '', 'draft', '"Up to date availability for {} can always be found at cf-ld.com/{}<br><br>".format(match(0), match(0).lower())', '', 'thread.default_reply()', '7', '', 'any'], [], ['add salutation if we have a draft', 'apply', '', 'automation', '', '', 'thread.has_existing_draft()', 'prepend_draft', '"{}<br><br>".format(thread.salutation())', '', 'thread.default_reply()', '8'], ['add signature if we have a draft', 'apply', '', 'automation', '', '', 'thread.has_existing_draft()', 'draft', '"{}".format(thread.signature())', '', 'thread.default_reply()', '9']])
        
        email_service = Mock()
        all_threads = [Thread(*get_thread_constructor_args('thread_test_inputs/one_email_thread.txt'), email_service)]
        email_service.get_all_threads = MagicMock(return_value=all_threads)
        email_service.get_label_name = MagicMock(return_value='Schools')
        email_service.set_label = MagicMock(return_value={'labelIds' : ['test label id']})
        email_service.get_user = MagicMock(return_value='tyler')
        email_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        email_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        draft_id = '1234'
        draft_msg_id = '2345'
        email_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        email_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : signature(all_threads[0]), 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(signature(all_threads[0]))}, 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}, {}))
        config = {}
        config['org'] = {}
        config['org']['name'] = 'example_org'
        config['org']['imports'] = ['from orgs.example_org.ExampleOrg import signature']
        logger = Logger('TestIntegration')
        m = Main([email_service], logger, config)

        m.run()

        # We'll process one email, add a label, and add a greeting and signature as a draft based on that label
        self.assertTrue('Schools' in all_threads[0].labels())
        self.assertTrue(all_threads[0].has_draft())
        # We'll look at the MimeMultipart we got on the last call to append_or_create_draft and confirm it's content
        mime_multipart, thread_id, called_draft_id = email_service.append_or_create_draft.call_args[0]

        self.assertEqual(all_threads[0].identifier, thread_id)
        self.assertEqual(draft_id, called_draft_id)
        self.assertEqual('tyler@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('tgaldes@gmail.com', mime_multipart['to'])
        self.assertEqual('test subject', mime_multipart['subject'])
        self.assertEqual('<CACUCK-BGnDjQ6QzU0cGKwLpHOnJoseTVjR1CNQ+yEubty=ar9A@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CACUCK-BGnDjQ6QzU0cGKwLpHOnJoseTVjR1CNQ+yEubty=ar9A@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(all_threads[0].salutation() + signature(all_threads[0]), mime_multipart.__dict__['_payload'][0].__dict__['_payload'])

