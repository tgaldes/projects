import pdb
from unittest.mock import MagicMock, Mock
import unittest

from framework.main import Main
from framework.Thread import Thread
from framework.Logger import Logger
from services.gmail.GMailMessage import GMailMessage

from test.TestUtil import get_thread_constructor_args, encode_for_payload
import test.TestConfig

from orgs.cfld.CfldOrg import direct_initialize_org
from orgs.cfld.test.CfldTestConfig import *
from orgs.example_org.ExampleOrg import header

class CfldIntegrationTest(unittest.TestCase):

    def test_new_submission_handler(self):

        rule_construction_data = [header, \
['test new submission handler', 'apply', '', 'automation/contact_form', '', '', 'len(thread) == 1', 'draft','run_new_submission_handler(thread)', '', 'thread.default_reply()', '1', '', '', '']]
        
        apply_service = Mock()
        apply_threads = [Thread(*get_thread_constructor_args('../orgs/cfld/test/integration_test_inputs/new_submission_only.txt'), apply_service)]
        apply_service.query = MagicMock(return_value=apply_threads)
        apply_service.get_user = MagicMock(return_value='apply')
        apply_service.get_email = MagicMock(return_value='apply@cleanfloorslockingdoors.com')
        apply_service.get_domains = MagicMock(return_value=['cleanfloorslockingdoors.com', 'cf-ld.com'])
        apply_service.get_label_name = MagicMock(return_value='automation/contact_form')

        draft_id = '1234'
        draft_msg_id = '2345'
        apply_service.get_drafts = MagicMock(return_value=[{'id' : draft_id, 'message' : {'id' : draft_msg_id}}])
        # Return an empty message instead of creating a brittle assert on how the new
        # submission handler will put together a response
        apply_service.append_or_create_draft = MagicMock(return_value=GMailMessage({'id' : draft_msg_id, 'snippet' : '', 'labelIds' : ['DRAFT'], 'payload' : {'body' : { 'data' : ''}, 'headers' : [{'name' : 'to', 'value' : '<test@mail.com>'}]}}, {}))
        apply_service.set_label = MagicMock(return_value={'labelIds' : ['test label id for "automation" label']})
        config = {}
        config['org'] = {}
        config['org']['name'] = 'cfld'
        config['org']['imports'] = ["from orgs.cfld.CfldOrg import run_new_submission_handler", \
                     "from orgs.cfld.util import get_new_application_email", \
                     "from orgs.cfld.util import signature", \
                     "from orgs.cfld.CfldOrg import lookup_info", \
                     "from orgs.cfld.CfldOrg import short_name_from_address", \
                     "from orgs.cfld.util import short_name_from_thread"]
        logger = Logger('TestIntegration')
        config['org_init_import'] = 'from orgs.cfld.CfldOrg import org_init'
        m = Main([apply_service], logger, config)
        # use our "bastard initialization"
        direct_initialize_org(rule_construction_data, raw_availability, raw_availability_blurbs, [])

        m.run()
        mime_multipart, thread_id, called_draft_id = apply_service.append_or_create_draft.call_args[0]
        self.assertIsNone(called_draft_id)
        self.assertEqual('apply@cleanfloorslockingdoors.com', mime_multipart['from'])
        self.assertTrue('djssi000000@gmail.com' in mime_multipart['to'])
        self.assertEqual('New submission for UCLA', mime_multipart['subject'])
        self.assertEqual('<74chIiUADxRa7A0JGOVDSDYu7bFzaKhAXvEsqilfXfQ@cleanfloorslockingdoors.com>', mime_multipart['In-Reply-To'])
        self.assertEqual('<74chIiUADxRa7A0JGOVDSDYu7bFzaKhAXvEsqilfXfQ@cleanfloorslockingdoors.com>', mime_multipart['References'])
        self.assertTrue(open_at_desired_move_in in mime_multipart.__dict__['_payload'][0].__dict__['_payload'])
        self.assertTrue(nothing_open in mime_multipart.__dict__['_payload'][0].__dict__['_payload'])


