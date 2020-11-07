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
            [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '0'], \
             ['subject match, draft action', 'apply', '', '', 'sregex', '', '', 'draft', 'value expression', '', 'dest expresssion', '1'], \
             ['unused rule- nothing in any matcher field', 'apply', '', '', '', '', '', 'draft', 'value expression', '', 'dest expresssion', '2'], \
             ['unused rule- no unused action', 'apply', '', '', 'sregex', '', '', 'unused', '', 'value expression', 'dest expresssion', '3']]

        rf = RuleFactory(sheet_data)

        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(2, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher))
        self.assertTrue(isinstance(rh.action, LabelAction))
        self.assertTrue(rh.action.unset)
        group = rule_groups[1]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, SubjectMatcher))
        self.assertTrue(isinstance(rh.action, DraftAction))
        self.assertEqual('value expression', rh.action.value)

    def test_need_inboxes_for_redirect(self):
        sheet_data = \
            [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group'], \
             ['redirect- wont be created since we dont specify inboxes', 'apply', 'tyler', 'automation', '', '', '', 'redirect', 'value_exp', 'finder_expr', 'dest_expr', '1']]

        rf = RuleFactory(sheet_data)
        with self.assertRaises(KeyError):
            # no rules created for the redirect since we didn't specify inbox objects
            rules = rf.get_rule_groups_for_user('apply')

        inboxes = {'apply' : 'apply_inbox', 'tyler' : 'tyler_inbox'}
        rf = RuleFactory(sheet_data, inboxes)
        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(1, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, LabelMatcher))
        self.assertTrue(isinstance(rh.action, RedirectAction))
        self.assertEqual('tyler_inbox', rh.action.inbox)

    def test_rule_grouping(self):
        sheet_data = \
            [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '2'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '2'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '3'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '4'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '4'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '3']]
        # final group sizes should be 3, 2, 1, 2

        rf = RuleFactory(sheet_data)
        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(4, len(rule_groups))
        self.assertEqual(3, len(rule_groups[0]))
        self.assertEqual(2, len(rule_groups[1]))
        self.assertEqual(1, len(rule_groups[2]))
        self.assertEqual(2, len(rule_groups[3]))

    def test_body_regex_matcher(self):
        sheet_data = \
            [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group'], \
             ['remove automation', 'apply', '', '', '', 'body regext', '', 'unlabel', '"automation"', '', '', '0']]

        rf = RuleFactory(sheet_data)

        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(1, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, BodyMatcher))
        self.assertTrue(isinstance(rh.action, LabelAction))
        self.assertTrue(rh.action.unset)
