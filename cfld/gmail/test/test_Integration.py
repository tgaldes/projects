import pdb
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
        email_service = Mock()
        all_threads = [Thread(*get_thread_constructor_args('integration_test_inputs/one_email_thread.txt'), email_service)]
        email_service.query = MagicMock(return_value=all_threads)
        email_service.get_label_name = MagicMock(return_value='Schools')
        email_service.set_label = MagicMock(return_value={'labelIds' : ['test label id']})
        email_service.get_all_history_ids = MagicMock(return_value={})
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
        config['org_init_import'] = 'from orgs.example_org.ExampleOrg import org_init'
        logger = Logger('TestIntegration')
        m = Main([email_service], logger, config)

        m.setup()
        m.run_one()

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


    def test_redirect(self):
    # We will see in tylers inbox that a tenant has submitted a rental application
    # We will look in the apply inbox for the thread of that tenant
    # We will create a draft in that thread under apply
        from orgs.example_org.ExampleOrg import header, signature 
        import orgs.example_org.ExampleOrg

        draft_text = 'I just processed the application'
        orgs.example_org.ExampleOrg.example_rule_construction_data = [header, \
['redirect', 'tyler', 'apply', '', 'Rental Application .*', '', '', 'redirect','"{}"'.format(draft_text), 'inbox.query(get_new_application_email(thread))', 'thread.default_reply()', '5', '', '']]

        tyler_service = Mock()
        tyler_threads = [Thread(*get_thread_constructor_args('integration_test_inputs/rental_application.txt'), tyler_service)]
        tyler_service.query = MagicMock(return_value=tyler_threads)
        tyler_service.get_user = MagicMock(return_value='tyler')
        tyler_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        tyler_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        tyler_service.get_all_history_ids = MagicMock(return_value={})

        apply_service = Mock()
        apply_threads = [Thread(*get_thread_constructor_args('integration_test_inputs/conversation_between_apply_inbox_and_tenant.txt'), apply_service)]
        apply_service.query = MagicMock(return_value=apply_threads)
        # We need to have this mocked so that the apply inbox can be searched
        apply_service.get_all_threads = MagicMock(return_value=apply_threads)
        apply_service.get_user = MagicMock(return_value='apply')
        apply_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        apply_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])

        draft_id = '1234'
        draft_msg_id = '2345'
        apply_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        apply_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : draft_text, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(draft_text)}, 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}, {}))
        apply_service.set_label = MagicMock(return_value={'labelIds' : ['test label id for "automation" label']})
        apply_service.get_all_history_ids = MagicMock(return_value={})
        config = {}
        config['org'] = {}
        config['org']['name'] = 'example_org'
        config['org']['imports'] = ['from orgs.example_org.ExampleOrg import signature', 'from orgs.example_org.ExampleOrg import get_new_application_email']
        config['org_init_import'] = 'from orgs.example_org.ExampleOrg import org_init'
        logger = Logger('TestIntegration')
        m = Main([tyler_service, apply_service], logger, config)

        m.setup()
        m.run_one()
        mime_multipart, thread_id, called_draft_id = apply_service.append_or_create_draft.call_args[0]
        self.assertIsNone(called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertEqual('tgaldes@gmail.com', mime_multipart['to'])
        self.assertEqual('New submission for USC', mime_multipart['subject'])
        self.assertEqual('<CACUCK-CJ6Aq-+i=h3bo5745o59FsfXQbfTX5xKeLFS7jM-JpGw@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CACUCK-CJ6Aq-+i=h3bo5745o59FsfXQbfTX5xKeLFS7jM-JpGw@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(draft_text, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])

        self.assertTrue(apply_threads[0].has_draft())
        self.assertTrue(draft_text in apply_threads[0].existing_draft_text())

    def test_lookup_info(self):
    # Use the lookup_info class to populate the draft and the draft destinations
        from orgs.example_org.ExampleOrg import header, signature 
        import orgs.example_org.ExampleOrg

        orgs.example_org.ExampleOrg.example_rule_construction_data = [header, \
['lookup_info_test', 'apply', '', 'Schools/(.*)', '', 'submitted my application', 'not thread.is_last_message_from_us()', 'draft','lookup_info("parking", match(0))', '', 'lookup_info("executed_leases", match(0))', '5', '', '']]
        
        school = 'USC'
        dest_email = 'lookup@one.com,lookup@two.com'
        parking_info = 'information about parking'

        apply_service = Mock()
        apply_threads = [Thread(*get_thread_constructor_args('integration_test_inputs/conversation_between_apply_inbox_and_tenant.txt'), apply_service)]
        apply_service.query = MagicMock(return_value=apply_threads)
        apply_service.get_user = MagicMock(return_value='apply')
        apply_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        apply_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        apply_service.get_label_name = MagicMock(return_value='Schools/USC')

        draft_id = '1234'
        draft_msg_id = '2345'
        apply_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        apply_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : parking_info, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(parking_info)}, 'headers' : [{'name' : 'to', 'value' : '<{}>,<{}>'.format(*dest_email.split(','))}]}}, {}))
        apply_service.set_label = MagicMock(return_value={'labelIds' : ['test label id for "automation" label']})
        apply_service.get_all_history_ids = MagicMock(return_value={})
        config = {}
        config['org'] = {}
        config['org']['name'] = 'example_org'
        config['org']['imports'] = ['from orgs.example_org.ExampleOrg import signature', 'from orgs.example_org.ExampleOrg import lookup_info']
        logger = Logger('TestIntegration')
        config['lookup_info'] = [['parking', school, parking_info], ['', 'UCLA', 'more info'], ['executed_leases', school, dest_email], ['', 'UCLA', 'otheremail@one.com']]
        config['org_init_import'] = 'from orgs.example_org.ExampleOrg import org_init'
        m = Main([apply_service], logger, config)

        m.setup()
        m.run_one()
        mime_multipart, thread_id, called_draft_id = apply_service.append_or_create_draft.call_args[0]
        self.assertIsNone(called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        for email in dest_email.split(','):
            self.assertTrue(email in mime_multipart['to'])
        self.assertEqual('New submission for USC', mime_multipart['subject'])
        self.assertEqual('<CACUCK-CJ6Aq-+i=h3bo5745o59FsfXQbfTX5xKeLFS7jM-JpGw@mail.gmail.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<CACUCK-CJ6Aq-+i=h3bo5745o59FsfXQbfTX5xKeLFS7jM-JpGw@mail.gmail.com>', mime_multipart['References'])
        self.assertEqual(parking_info, mime_multipart.__dict__['_payload'][0].__dict__['_payload'])


        self.assertTrue('Schools/{}'.format(school) in apply_threads[0].labels())
        self.assertTrue(apply_threads[0].has_draft())
        self.assertTrue(parking_info in apply_threads[0].existing_draft_text())

    def test_catch_socket_timeout_exception_in_main(self):
    # In this test we'll have a mock service that raises an exception the first time we add a draft
    # We expect that 
        from orgs.example_org.ExampleOrg import signature
        email_service = Mock()
        all_threads = [Thread(*get_thread_constructor_args('integration_test_inputs/one_email_thread.txt'), email_service)]
        email_service.query = MagicMock(return_value=all_threads)
        email_service.get_label_name = MagicMock(return_value='Schools')
        email_service.set_label = MagicMock(return_value={'labelIds' : ['test label id']})
        email_service.get_all_history_ids = MagicMock(return_value={})
        email_service.get_user = MagicMock(return_value='tyler')
        email_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        email_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        draft_id = '1234'
        draft_msg_id = '2345'
        email_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        email_service.append_or_create_draft = MagicMock(side_effect=Exception)
        config = {}
        config['org'] = {}
        config['org']['name'] = 'example_org'
        config['org']['imports'] = ['from orgs.example_org.ExampleOrg import signature']
        config['org_init_import'] = 'from orgs.example_org.ExampleOrg import org_init'
        logger = Logger('TestIntegration')
        m = Main([email_service], logger, config)

        m.setup()
        # if we don't catch the exception here we'll fail
        m.run_one()
        self.assertEqual(1, email_service.append_or_create_draft.call_count)

