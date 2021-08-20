from unittest.mock import MagicMock, Mock
import unittest
import test.TestConfig

from framework.RuleGroup import *

rule_group_type_enums = ['yes', 'yes2']
user = 'user'
class TestRuleGroupBase(RuleGroup):
    def __init__(self, rules, query, user):
        super(TestRuleGroupBase, self).__init__(rules, 'child', query, user)
    def _enums(self):
        return rule_group_type_enums

class RuleGroupTest(unittest.TestCase):
    
    def test_basic(self):
        # only first rule needs to specify
        l = [('', 'yes', ''), ('', '', '')]
        t = TestRuleGroupBase(l, '', user)
        # any of the enum values can match
        l = [('', 'yes2', ''), ('', '', '')]
        t = TestRuleGroupBase(l, '', user)
        # first doesn't specify
        l = [('', '', ''), ('', 'yes', '')]
        with self.assertRaises(Exception):
            t = TestRuleGroupBase(l, '', user)
        # later enum value doesn't match
        l = [('', 'yes2', ''), ('', 'yes', ''), ('', 'no match', '')]
        with self.assertRaises(Exception):
            t = TestRuleGroupBase(l, '', user)


class IfElseRuleGroupTest(unittest.TestCase):

    def test_basic(self):
        mock_irule = Mock()
        mock_irule.process = MagicMock()
        t = {}
        ieg = IfElseRuleGroup([(mock_irule, '', '')], '', user)
        ieg.process(t)
        mock_irule.process.assert_called_once_with(t)

    def test_break_after_one_true(self):
        mock_irule_1 = Mock()
        mock_irule_1.process = MagicMock(return_value=False)
        mock_irule_2 = Mock()
        mock_irule_2.process = MagicMock(return_value=True)
        mock_irule_3 = Mock()
        mock_irule_3.process = MagicMock(return_value=False)
        t = {}
        ieg = IfElseRuleGroup([(mock_irule_1, '', ''), (mock_irule_2, '', ''), (mock_irule_3, '', '')], '', user)
        ieg.process(t)
        mock_irule_1.process.assert_called_once_with(t)
        mock_irule_2.process.assert_called_once_with(t)
        self.assertEqual(0, mock_irule_3.process.call_count)
        self.assertEqual(user, ieg.get_user())

    def test_throw_in_constructor(self):
        mock_irule = Mock()
        t = {}
        with self.assertRaises(Exception):
            ieg = IfElseRuleGroup()

    def test_base_validate(self):
        mock_irule_1 = Mock()
        # Even though the first rule returns true, the later rule will process the thread
        mock_irule_1.process = MagicMock(return_value=True)
        mock_irule_2 = Mock()
        mock_irule_2.process = MagicMock(return_value=True)
        t = {}
        ieg = IfElseRuleGroup([(mock_irule_1, '', ''), (mock_irule_2, '', '')], '', user)
        BaseValidator.set_validate_mode(True)
        ieg.process(t)
        mock_irule_1.process.assert_called_once_with(t)
        mock_irule_2.process.assert_called_once_with(t)
        BaseValidator.set_validate_mode(False)

class IfAnyRuleGroupTest(unittest.TestCase):

    def test_if_and_all_any(self):
        mock_irule_1 = Mock()
        mock_irule_1.process = MagicMock(return_value=False)
        mock_irule_2 = Mock()
        mock_irule_2.process = MagicMock(return_value=True)
        mock_irule_3 = Mock()
        mock_irule_3.process = MagicMock(return_value=False)
        mock_irule_4 = Mock()
        mock_irule_4.process = MagicMock(return_value=True)
        mock_irule_5 = Mock()
        mock_irule_5.process = MagicMock(return_value=True)
        iag = IfAnyRuleGroup([(mock_irule_1, 'ifany', 'if'), (mock_irule_2, '', 'if'), (mock_irule_3, '', 'if'), (mock_irule_4, '', 'any'), (mock_irule_5, '', 'any')], '', user)
        t = {}
        iag.process(t)
        mock_irule_1.process.assert_called_once_with(t)
        mock_irule_2.process.assert_called_once_with(t)
        self.assertEqual(0, mock_irule_3.process.call_count, 0)
        mock_irule_4.process.assert_called_once_with(t)
        mock_irule_5.process.assert_called_once_with(t)
        self.assertEqual(user, iag.get_user())

    def test_no_if_no_any(self):
        mock_irule_1 = Mock()
        mock_irule_1.process = MagicMock(return_value=False)
        mock_irule_2 = Mock()
        mock_irule_2.process = MagicMock(return_value=False)
        mock_irule_3 = Mock()
        mock_irule_3.process = MagicMock(return_value=False)
        mock_irule_4 = Mock()
        mock_irule_4.process = MagicMock(return_value=True)
        mock_irule_5 = Mock()
        mock_irule_5.process = MagicMock(return_value=True)
        iag = IfAnyRuleGroup([(mock_irule_1, 'ifany', 'if'), (mock_irule_2, '', 'if'), (mock_irule_3, '', 'if'), (mock_irule_4, '', 'any'), (mock_irule_5, '', 'any')], '', user)
        t = {}
        iag.process(t)
        mock_irule_1.process.assert_called_once_with(t)
        mock_irule_2.process.assert_called_once_with(t)
        mock_irule_3.process.assert_called_once_with(t)
        self.assertEqual(0, mock_irule_4.process.call_count)
        self.assertEqual(0, mock_irule_5.process.call_count)

    def test_throw_in_constructor(self):
        mock_irule = Mock()
        # Non enum value
        with self.assertRaises(Exception):
            iag = IfAnyRuleGroup([(mock_irule_2, 'ifany', 'if'), (mock_irule_2, '', 'any'), (mock_irule_2, '', 'not enum val')], '', user)
        # No if rules
        with self.assertRaises(Exception):
            iag = IfAnyRuleGroup([(mock_irule_2, 'ifany', 'any'), (mock_irule_2, '', 'any'), (mock_irule_2, '', 'any')], '', user)
        # No any rules
        with self.assertRaises(Exception):
            iag = IfAnyRuleGroup([(mock_irule_2, 'ifany', 'if'), (mock_irule_2, '', 'if'), (mock_irule_2, '', 'if')], '', user)
        # if rule after any rule
        with self.assertRaises(Exception):
            iag = IfAnyRuleGroup([(mock_irule_2, 'ifany', 'if'), (mock_irule_2, '', 'any'), (mock_irule_2, '', 'if')], '', user)

class SingleRuleGroupTest(unittest.TestCase):

    def test_basic(self):
        mock_irule = Mock()
        mock_irule.process = MagicMock()
        t = {}
        srg = SingleRuleGroup([(mock_irule, '', '')], '', user)
        srg.process(t)
        mock_irule.process.assert_called_once_with(t)
        self.assertEqual(user, srg.get_user())

    def test_throw_in_constructor(self):
        mock_irule = Mock()
        t = {}
        with self.assertRaises(Exception):
            srg = SingleRuleGroup([(mock_irule, '', ''), (mock_irule, '', '')], '', user)
        with self.assertRaises(Exception):
            srg = SingleRuleGroup()

    # We are ok with a user specifying they want to create an ifelse rule group
    # and only having one rule in that group. Single rule group == if else rule
    # group with one rule
    def test_ifelse_type_specified(self):
        mock_irule = Mock()
        mock_irule.process = MagicMock()
        t = {}
        srg = SingleRuleGroup([(mock_irule, 'ifelse', '')], '', user)
        srg.process(t)
        mock_irule.process.assert_called_once_with(t)

if __name__=='__main__':
    unittest.main()




