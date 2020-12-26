from interface import implements
import copy
import pdb

from framework.RuleHolder import RuleHolder
from framework.Interfaces import IRule
from framework.Logger import Logger
from framework.BaseValidator import BaseValidator


# When we have more enum type values we can extract them somewhere else
if_any_rule_types = ['if', 'any']

class RuleGroup(BaseValidator):
    def __init__(self, rules_tup, child, query):
        super(RuleGroup, self).__init__(child)
        enums = copy.copy(self._enums())
        for i, (_, group_type, unused) in enumerate(rules_tup):
            if i == 1: # only the first row needs to specify the type
                enums.append('')
            if group_type not in enums:
                raise Exception('group_type: {} passed in error'.format(group_type))
        self.query = query

    def _enums(self):
        raise Exception('Implement _enums in child RuleGroup')
        # REFACTOR: overriding functions should be returning enum values

    def get_query(self):
        return self.query

# When the first irule matches the thread, we break
class IfElseRuleGroup(implements(IRule), RuleGroup):
    def __init__(self, rules_tup, query):
        super(IfElseRuleGroup, self).__init__(rules_tup, __class__, query)
        self.rules = []
        for irule, _, rule_type in rules_tup:
            self.rules.append(irule)
        if not self.rules:
            raise Exception('Cannot create with empty rule list')
        self.li('Created IfElseRuleGroup')

    def __getitem__(self, key):
        if key < 0:
            raise IndexError('Negative indexing not supported')
        return self.rules[key]

    def __len__(self):
        return len(self.rules)

    def process(self, thread):
        for irule in self.rules:
            rule_match = irule.process(thread)
            # in validate mode we want to pass the thread to every rule
            if super().force_match():
                continue
            elif rule_match:
                break

    def _enums(self):
        return ['', 'ifelse']


# Do the if actions until one returns true
# If any if actions returned true, do all the then actions
class IfAnyRuleGroup(implements(IRule), RuleGroup):
    def __init__(self, rules_tup, query):
        super(IfAnyRuleGroup, self).__init__(rules_tup, __class__, query)
        self.if_rules = []
        self.any_rules = []
        for irule, _, rule_type in rules_tup:
            if rule_type == if_any_rule_types[0]:
                self.if_rules.append(irule)
            elif rule_type == if_any_rule_types[1]:
                self.any_rules.append(irule)
            else:
                raise Exception('unknown if any rule type: {}'.format(rule_type))
        if not self.if_rules or not self.any_rules:
            raise Exception('Cannot create with empty if rule list: {} or any rule list: {}'.format(self.if_rules, self.any_rules))
        self.li('Created IfAnyRuleGroup')

    def __len__(self):
        return len(self.if_rules) + len(self.any_rules)

    def __getitem__(self, key):
        if key < 0:
            raise IndexError('Negative indexing not supported')
        if len(self.if_rules) <= key:
            return self.any_rules[key]
        return self.if_rules[key]

    def process(self, thread):
        match = False
        for irule in self.if_rules:
            if irule.process(thread):
                match = True
                # in validate mode we want to pass the thread to every rule
                if super().force_match():
                    continue
                elif match:
                    break

        if match or super().force_match():
            for i, irule in enumerate(self.any_rules):
                if not irule.process(thread):
                    raise Exception('any_rule {} at index {} did not match thread with id: {} subject: {}'.format(irule, i, thread.field('id'), thread.subject())) 

    def _enums(self):
        return ['ifany']


class SingleRuleGroup(implements(IRule), RuleGroup):
    def __init__(self, rules_tup, query):
        super(SingleRuleGroup, self).__init__(rules_tup, __class__, query)
        if len(rules_tup) != 1:
            raise Exception('Cannot create with rule list of size != 1: {}'.format(rules_tup))
        self.rule = rules_tup[0][0]
        self.li('Created SingleRuleGroup')

    def _enums(self):
        return ['']

    def __len__(self):
        return 1

    def __getitem__(self, key):
        if key != 0:
            raise IndexError('Negative indexing not supported')
        return self.rule

    def process(self, thread):
        self.rule.process(thread)
