from unittest.mock import MagicMock, Mock
import unittest
import NewLogger
NewLogger.global_log_level = 'DEBUG'

from RuleFactory import RuleFactory
from Matchers import *
from Actions import *

class RuleFactoryTest(unittest.TestCase):
    def test_create_rules(self):
        sheet_data = \
            [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'body'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', ''], \
             ['subject match, draft action', 'apply', '', '', 'sregex', '', '', 'draft', '', '', 'dest expresssion', 'body expression'], \
             ['unused rule- nothing in any matcher field', 'apply', '', '', '', '', '', 'draft', '', '', 'dest expresssion', 'body expression'], \
             ['unused rule- no unused action', 'apply', '', '', 'sregex', '', '', 'unused', '', '', 'dest expresssion', 'body expression']]

        rf = RuleFactory(sheet_data)

        rules = rf.get_rules_for_user('apply')
        self.assertEqual(2, len(rules))
        rh = rules[0]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher))
        self.assertTrue(isinstance(rh.action, LabelAction))
        self.assertTrue(rh.action.unset)
        rh = rules[1]
        self.assertTrue(isinstance(rh.matcher, SubjectMatcher))
        self.assertTrue(isinstance(rh.action, DraftAction))


    def test_need_inboxes_for_redirect(self):
        sheet_data = \
            [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'body'], \
             ['redirect- wont be created since we dont specify inboxes', 'apply', 'tyler', 'automation', '', '', '', 'redirect', '', 'finder_expr', 'dest_expr', 'body_expr']]

        rf = RuleFactory(sheet_data)
        with self.assertRaises(KeyError):
            # no rules created for the redirect since we didn't specify inbox objects
            rules = rf.get_rules_for_user('apply')


        inboxes = {'apply' : 'apply_inbox', 'tyler' : 'tyler_inbox'}
        rf = RuleFactory(sheet_data, inboxes)
        rules = rf.get_rules_for_user('apply')
        self.assertEqual(1, len(rules))
        rh = rules[0]
        self.assertTrue(isinstance(rh.matcher, LabelMatcher))
        self.assertTrue(isinstance(rh.action, RedirectAction))
        self.assertEqual('tyler_inbox', rh.action.inbox)
