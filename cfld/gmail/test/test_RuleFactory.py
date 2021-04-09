from unittest.mock import MagicMock, Mock
import unittest
import test.TestConfig

from framework.RuleFactory import RuleFactory
from framework.RuleGroup import IfElseRuleGroup, IfAnyRuleGroup, SingleRuleGroup
from framework.Matchers import BodyMatcher, ComboMatcher, SubjectMatcher, AllMatcher, LabelMatcher
from framework.Actions import LabelAction, DraftAction, RedirectAction, AttachmentAction, LabelLookupAction, ForwardAttachmentAction

class RuleFactoryTest(unittest.TestCase):
    header = ['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group', 'group_type', 'rule_type', 'query']
    def test_create_rules(self):
        sheet_data = \
            [RuleFactoryTest.header, \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '0', '', '', ''], \
             ['subject match, draft action', 'apply', '', '', 'sregex', '', '', 'draft', 'value expression', '', 'dest expresssion', '1', '', '', ''], \
             ['match anything', 'apply', '', '', '', '', '', 'draft', 'value expression', '', 'dest expresssion', '2', '', '', '']]

        rf = RuleFactory(sheet_data)

        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(3, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher))
        self.assertTrue(isinstance(rh.action, LabelAction))
        self.assertTrue(rh.action.unset)
        group = rule_groups[1]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher))
        self.assertTrue(isinstance(rh.action, DraftAction))
        self.assertEqual('value expression', rh.action.value)
        group = rule_groups[2]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, LabelMatcher))
        self.assertTrue(isinstance(rh.action, DraftAction))
        self.assertEqual('value expression', rh.action.value)

    # We have this very throw heavy so users are warned asap about bad configuration 
    # of their rules
    def test_throw_for_bad_setup(self):
        # Throw for no inboxes passed when we try to create redirect rules
        sheet_data = \
            [RuleFactoryTest.header, \
             ['redirect- wont be created since we dont specify inboxes', 'apply', 'tyler', 'automation', '', '', '', 'redirect', 'value_exp', 'finder_expr', 'dest_expr', '1', '']]
        with self.assertRaises(Exception):
            rf = RuleFactory(sheet_data)
        # Bad action name
        sheet_data = \
            [RuleFactoryTest.header, \
             ['match anything', 'apply', '', '', '', '', '', 'I dont know how to create an action for this string', 'value expression', '', 'dest expresssion', '2', '', '', '']]
        with self.assertRaises(Exception):
            rf = RuleFactory(sheet_data)
        # no rule user specified
        sheet_data = \
            [RuleFactoryTest.header, \
             ['match anything', '', '', '', '', '', '', 'draft', 'value expression', '', 'dest expresssion', '2', '', '', '']]
        with self.assertRaises(Exception):
            rf = RuleFactory(sheet_data)
        # group number does down 
        sheet_data = \
            [RuleFactoryTest.header, \
             ['match anything', '', '', '', '', '', '', 'draft', 'value expression', '', 'dest expresssion', '2', '', ''], \
             ['match anything', '', '', '', '', '', '', 'draft', 'value expression', '', 'dest expresssion', '1', '', '', '']]
        with self.assertRaises(Exception):
            rf = RuleFactory(sheet_data)
        # group number not interpretable as float
        sheet_data = \
            [RuleFactoryTest.header, \
             ['match anything', '', '', '', '', '', '', 'draft', 'value expression', '', 'dest expresssion', '2.a', '', '', '']]
        with self.assertRaises(Exception):
            rf = RuleFactory(sheet_data)

    def test_need_inboxes_for_redirect(self):
        sheet_data = \
            [RuleFactoryTest.header, \
             ['redirect- wont be created since we dont specify inboxes', 'apply', 'tyler', 'automation', '', '', '', 'redirect', 'value_exp', 'finder_expr', 'dest_expr', '1']]

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

    def test_rule_grouping_and_types(self):
        sheet_data = \
            [RuleFactoryTest.header, \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1', '', ''], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1', '', ''], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '1', '', ''], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '2', 'ifany', 'if'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '2', '', 'any'], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '3', '', ''], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '4', 'ifelse', ''], \
             ['remove automation', 'apply', '', 'automation', '', '', 'not thread.has_existing_draft()', 'unlabel', '"automation"', '', '', '4', 'ifelse', '', '']]
        # final group sizes should be 3, 2, 1, 2
        # types are ifelse, ifany, single, ifany

        rf = RuleFactory(sheet_data)
        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(4, len(rule_groups))
        self.assertEqual(3, len(rule_groups[0]))
        self.assertEqual(2, len(rule_groups[1]))
        self.assertEqual(1, len(rule_groups[2]))
        self.assertEqual(2, len(rule_groups[3]))
        self.assertTrue(isinstance(rule_groups[0], IfElseRuleGroup))
        self.assertTrue(isinstance(rule_groups[1], IfAnyRuleGroup))
        self.assertTrue(isinstance(rule_groups[2], SingleRuleGroup))
        self.assertTrue(isinstance(rule_groups[3], IfElseRuleGroup))

    def test_body_regex_matcher(self):
        sheet_data = \
            [RuleFactoryTest.header, \
             ['remove automation', 'apply', '', '', '', 'body regext', '', 'unlabel', '"automation"', '', '', '0', '', '', '']]

        rf = RuleFactory(sheet_data)

        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(1, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, BodyMatcher))
        self.assertTrue(isinstance(rh.action, LabelAction))
        self.assertTrue(rh.action.unset)

    def test_prepend_draft_action(self):
        sheet_data = \
            [RuleFactoryTest.header, \
             ['remove automation', 'apply', '', '', '', 'body regext', '', 'prepend_draft', '"automation"', '', 'destination_email', '0', '', '', '']]

        rf = RuleFactory(sheet_data)

        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(1, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(1, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher))
        self.assertTrue(isinstance(rh.action, DraftAction))
        self.assertTrue(rh.action.prepend)

    def test_attachement_forward_attachement_label_lookup_creation(self):
        sheet_data = \
            [RuleFactoryTest.header, \
            # basic attachment with a filename
             ['attachment', 'apply', '', '', '', 'body regext', '', 'attachment', '/home/tgaldes/Pictures/*txt', '', 'destination_email', '0', '', '', ''], \
            # attach from existing thread attachments
             ['forward attachment', 'apply', '', '', '', 'body regext', '', 'forward_attachment', '', '', 'destination_email', '0', '', '', ''], \
            # label lookup
             ['remove automation', 'apply', 'tyler', '', '', 'body regext', '', 'label_lookup', 'Schools/.*', 'inbox.query(get_approved_application_name(thread))', '', '0', '', '', '']]

        inboxes = {'apply' : 'apply_inbox', 'tyler' : 'tyler_inbox'}
        rf = RuleFactory(sheet_data, inboxes)

        rule_groups = rf.get_rule_groups_for_user('apply')
        self.assertEqual(1, len(rule_groups))
        group = rule_groups[0]
        self.assertEqual(3, len(group))
        rh = group[0]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher)) # body & reverse label
        self.assertTrue(isinstance(rh.action, AttachmentAction))
        rh = group[1]
        self.assertTrue(isinstance(rh.matcher, ComboMatcher))
        self.assertTrue(isinstance(rh.action, ForwardAttachmentAction))
        rh = group[2]
        self.assertTrue(isinstance(rh.matcher, BodyMatcher))
        self.assertTrue(isinstance(rh.action, LabelLookupAction))

    def test_only_specify_query_on_first_rule_of_rule_group(self):
        sheet_data = \
            [RuleFactoryTest.header, \
             ['remove automation', 'apply', '', '', '', 'body regext', '', 'prepend_draft', '"automation"', '', 'destination_email', '0', '', '', 'label:automation'], \
             ['remove automation', 'apply', '', '', '', 'body regext', '', 'prepend_draft', '"automation"', '', 'destination_email', '0', '', '', 'label:automation']]
        with self.assertRaises(Exception):
            rf = RuleFactory(sheet_data)








