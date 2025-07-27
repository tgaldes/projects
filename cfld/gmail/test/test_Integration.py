import pdb
from unittest.mock import MagicMock, Mock
import unittest

from framework.main import Main
from framework.Thread import Thread
from framework.Logger import Logger
from services.gmail.GMailMessage import GMailMessage

from test.TestUtil import get_thread_constructor_args, encode_for_payload
from framework.Config import Config

class IntegrationTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(IntegrationTest, self).__init__(*args, **kwargs)
        self.config_dict = {'long_signature' : 'This is a long signature', 'short_signature' : 'short sig'}

        self.config = Config()
        self.config.initialize(None, self.config_dict)
        self.config_dict = {'long_signature' : 'This is a long signature', 'short_signature' : 'short sig'}

    def test_dummy(self):
        
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
        email_service.send_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : signature(all_threads[0]), 'labelIds' : ['SENT'], 'payload' : {'body' : { 'data' : encode_for_payload(signature(all_threads[0]))}, 'headers' : [{'name' : 'to', 'value' : 'Tyler Galdes <tgaldes@gmail.com>'}]}}, {}))
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

        # now let's send the draft that we created
        self.assertEqual(1, len(all_threads[0])) # len doesn't count draft messages
        all_threads[0].send_draft()
        self.assertFalse(all_threads[0].has_draft())
        self.assertEqual(2, len(all_threads[0]))
        sent_draft_id = email_service.send_draft.call_args[0][0]
        self.assertEqual(draft_id, sent_draft_id)


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

    def test_catch_exception_on_individual_thread_and_blacklist(self):
    # two rules- one to label everything, one to add a draft to everything
    # two threads. the first will throw when we try to add a label to it
    # we expect to catch that exception and not process that thread any more
    # we'll end up with no drafts on the bad thread, and add a label and a draft to the good thread

        test_draft_text = 'test draft'
        from orgs.example_org.ExampleOrg import header
        example_rule_construction_data = [header, \
        # label rule, will always match .* and run
            ['Label by school', 'tyler', '', '', '', '', '', 'draft', test_draft_text, '', '', '1', 'ifelse', ''], \
        # draft rule, will always match empty matcher
            ['add draft', 'tyler', '', '', '', '', '', 'draft', test_draft_text, '', 'thread.default_reply()', '2', '', '', '']]

        good_service = Mock()
        bad_service = Mock()
        bad_thread = Thread(*get_thread_constructor_args('integration_test_inputs/one_email_thread.txt'), bad_service)
        good_thread = Thread(*get_thread_constructor_args('integration_test_inputs/rental_application.txt'), good_service)
        all_threads = [bad_thread, good_thread]


        # set up good service
        good_service.query = MagicMock(return_value=all_threads)
        good_service.get_label_name = MagicMock(return_value='Schools')
        good_service.set_label = MagicMock(return_value={'labelIds' : ['test label id']})
        good_service.get_all_history_ids = MagicMock(return_value={})
        good_service.get_user = MagicMock(return_value='tyler')
        good_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        good_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])

        draft_id = '1234'
        draft_msg_id = '2345'
        good_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        dest_email = 'lookup@one.com,lookup@two.com'
        good_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : test_draft_text, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(test_draft_text)}, 'headers' : [{'name' : 'to', 'value' : '<{}>,<{}>'.format(*dest_email.split(','))}]}}, {}))

        # set up bad service, will throw on create_or_append_draft
        bad_service.query = MagicMock(return_value=all_threads)
        bad_service.get_label_name = MagicMock(return_value='Schools')
        bad_service.set_label = MagicMock(return_value={'labelIds' : ['test label id']})
        bad_service.get_all_history_ids = MagicMock(return_value={})
        bad_service.get_user = MagicMock(return_value='tyler')
        bad_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        bad_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])

        draft_id = '1234'
        draft_msg_id = '2345'
        bad_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        bad_service.append_or_create_draft = MagicMock(side_effect=Exception)

        config = {}
        config['org'] = {}
        config['org']['name'] = 'example_org'
        config['org']['imports'] = ['from orgs.example_org.ExampleOrg import signature']
        config['org_init_import'] = 'from orgs.example_org.ExampleOrg import org_init'
        logger = Logger('TestIntegration')
        m = Main([good_service, bad_service], logger, config)

        m.setup()
        # if we don't catch the exception here we'll fail
        m.run_one()

        self.assertEqual(2, good_service.append_or_create_draft.call_count)
        self.assertEqual(2, good_service.set_label.call_count) # will set the label as 'automation' twice
        self.assertEqual(1, bad_service.set_label.call_count) # got hit once while setting the label for automation/errors
        self.assertTrue(bad_thread.id() in m.inboxes['tyler'].blacklisted_thread_ids)
        self.assertEqual(1, len(m.inboxes['tyler'].blacklisted_thread_ids))

    def test_open_ai_response(self):
        pass

    def test_reinitialize_thread_mid_iteration(self):
        # This is a complicated example
        # we are in the middle of processing rules
        # a new message comes in on a thread that has the label asdf that we already cached on the service
        # we process a few more rules
        # now we have a rule that does a custom query 'label:asdf'
        # the service will see that it needs to get the full thread from the service
        # and reinitialize it
        # now we come to the end of the run
        # we can't finalize that threads history id! since it came in mid run
        # we'll have missed rules early on that might have wanted to act on it
        # and thus need to give it another chance to be processed


        # in the test we've boiled this down to initializing the thread
        # with reinit set to True. We'll process all the rules three times,
        # and only after the second iteration will the history id be marked as finalized,
        # so we expect to add the draft twice

        test_draft_text = '"test draft"'
        from orgs.example_org.ExampleOrg import header
        import orgs.example_org.ExampleOrg
        orgs.example_org.ExampleOrg.example_rule_construction_data = [header, \
        # draft rule, will always match empty matcher
            ['add draft', 'tyler', '', '', '', '', '', 'draft', test_draft_text, '', 'thread.default_reply()', '2', '', '', 'custom_query']]

        reinit_service = Mock()
        reinit_thread = Thread(*get_thread_constructor_args('integration_test_inputs/one_email_thread.txt'), reinit_service)
        all_threads = [reinit_thread]

        # set up reinit service
        #reinit_service.query = MagicMock(return_value=all_threads)
        reinit_service.query = MagicMock(return_value=all_threads)
        reinit_service.get_label_name = MagicMock(return_value='Schools')
        reinit_service.set_label = MagicMock(return_value={'labelIds' : ['test label id']})
        current_history_id = 1
        reinit_service.get_all_history_ids = MagicMock(return_value={reinit_thread.id() : current_history_id})
        reinit_thread.history_id = MagicMock(return_value=current_history_id)
        reinit_service.get_user = MagicMock(return_value='tyler')
        reinit_service.get_email = MagicMock(return_value='tyler@cleanfloorslockingdoors.com')
        reinit_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])

        draft_id = '1234'
        draft_msg_id = '2345'
        dest_email = 'lookup@one.com,lookup@two.com'
        reinit_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        reinit_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : test_draft_text, 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : encode_for_payload(test_draft_text)}, 'headers' : [{'name' : 'to', 'value' : '<{}>,<{}>'.format(*dest_email.split(','))}]}}, {}))

        config = {}
        config['org'] = {}
        config['org']['name'] = 'example_org'
        config['org']['imports'] = ['from orgs.example_org.ExampleOrg import signature']
        config['org_init_import'] = 'from orgs.example_org.ExampleOrg import org_init'
        logger = Logger('TestIntegration', '/cfld/log/test/', True)
        m = Main([reinit_service], logger, config)

        m.setup()

        # first run
        # will have nothing finalized so will execute the rule
        # afterwards 1 is finalized as the history id
        m.run_one()
        self.assertEqual(1, reinit_service.append_or_create_draft.call_count)

        current_history_id = 2
        #reinit_thread.history_id = MagicMock(return_value=current_history_id)
        reinit_service.get_all_history_ids = MagicMock(return_value={})
        reinit_thread.history_id = MagicMock(return_value=2)
        # 1 is finalized but we return 2 as the current history id
        # so the rule executes
        # afterwards, we don't give any new history id to finalize
        m.run_one()
        self.assertEqual(2, reinit_service.append_or_create_draft.call_count)

        reinit_service.get_all_history_ids = MagicMock(return_value={reinit_thread.id() : current_history_id})
        # 1 is STILL finalized but we return 2 as the current history id
        # so the rule executes
        # afterwards, we finalize 2
        m.run_one()
        self.assertEqual(3, reinit_service.append_or_create_draft.call_count)

        # 2 is finalized and we return 2 as the history id,
        # so query won't return the thread
        m.run_one()
        self.assertEqual(3, reinit_service.append_or_create_draft.call_count)

