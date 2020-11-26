from Matchers import *
from Actions import *
import collections
from Logger import Logger
from RuleHolder import RuleHolder
from RuleGroup import IfAnyRuleGroup, IfElseRuleGroup, SingleRuleGroup

def row_is_empty(row):
    for item in row:
        if item:
            return False
    return True

class RuleFactory(Logger):
    # sheet data is a list of lists
    # first list is the header which we'll use to create a named tuple
    # then for each row we'll create an instance of the desired RuleHolder
    def __init__(self, sheet_data=[], inboxes={}):
        super(RuleFactory, self).__init__(__name__)
        if len(sheet_data) < 2:
            raise Exception('Tried to construct RuleFactory with data that is only {} row.'.format(len(sheet_data)))
        RuleTuple = collections.namedtuple('RuleTuple', sheet_data[0])
        header_size = len(sheet_data[0])
        last_group_index = -1
        # List of [(Group, user)..... so we can process in order of the rule groups
        raw_rule_group_tuples = []
        for rule_row in sheet_data[1:]:
            if row_is_empty(rule_row):
                continue
            log_msg = 'Created: '
            # Google will trim rows when there isn't data in some of the last fields,
            # so insert empty strings here to keep our named tuple happy
            rule_row.extend(['' for x in range(header_size - len(rule_row))])

            tup = RuleTuple(*rule_row)
            if not tup.group or not (int(tup.group) == last_group_index or last_group_index < int(tup.group)):
                self.lw('Cannot specify a group index of {} when last group index was {}'.format(tup.group, last_group_index))
                continue
            if not tup.email:
                self.lw('Cannot create a rule without a user specified.')
                continue
            matchers = []
            # create matcher
            if tup.label_regex:
                matchers.append(LabelMatcher(tup.label_regex))
                log_msg += 'LabelMatcher, '
            if tup.subject_regex:
                matchers.append(SubjectMatcher(tup.subject_regex))
                log_msg += 'SubjectMatcher, '
            if tup.body_regex:
                matchers.append(BodyMatcher(tup.body_regex))
                log_msg += 'BodyMatcher, '
            if tup.expression_match:
                matchers.append(ExpressionMatcher(tup.expression_match))
                log_msg += 'ExpressionMatcher, '
            if not matchers:
                matchers.append(AllMatcher())
                log_msg += 'AllMatcher, '
            # create action
            if tup.action == 'draft':
                action = DraftAction(tup.value, tup.destinations)
                log_msg += 'DraftAction'
            elif tup.action == 'prepend_draft':
                action = DraftAction(tup.value, tup.destinations, prepend=True)
                log_msg += 'DraftAction'
            elif tup.action == 'label':
                action = LabelAction(tup.value)
                log_msg += 'LabelAction'
            elif tup.action == 'unlabel':
                action = LabelAction(tup.value, unset=True)
                log_msg += 'UnlabelAction'
            elif tup.action == 'remove_draft':
                action = RemoveDraftAction()
                log_msg += 'RemoveDraftAction'
            elif tup.action == 'redirect':
                if tup.dest_email not in inboxes:
                    self.lw('RuleFactory doesn\'t have an inbox configured for dest_email: {}, no rule will be created'.format(tup.dest_email))
                    continue
                action = RedirectAction(inboxes[tup.dest_email], tup.finder, tup.value, tup.destinations)
                log_msg += 'RedirectAction'
            elif tup.action == 'empty':
                action = EmptyAction()
                log_msg += 'EmptyAction'
            else:
                self.lw('Only draft, prepend_draft, label, unlabel, remove_draft, and redirect are supported for actions. No rule will be created for {}.'.format(tup.action))
                continue

            # Create the rule holder
            if len(matchers) == 1:
                rh = RuleHolder(action, matchers[0])
            else:
                rh = RuleHolder(action, ComboMatcher(matchers))

            # Add the (RuleHolder, type, rule_type) tuple # TODO
            if int(tup.group) == last_group_index:
                raw_rule_group_tuples[-1][0].append((rh, tup.group_type, tup.rule_type))
            else: # group of one rule
                raw_rule_group_tuples.append(([(rh, tup.group_type, tup.rule_type)], tup.email))
            last_group_index = int(tup.group)

            log_msg += ', Group #{}'.format(tup.group)

            self.li(log_msg)

        self.all_rule_groups = []
        self.__create_rule_groups(raw_rule_group_tuples, self.all_rule_groups)

    def __create_rule_groups(self, tups, target_list):         
        for raw_rule_group, user in tups:
            if not raw_rule_group:
                raise Exception('raw_rule_group of size 0')
            if len(raw_rule_group) == 1:
                target_list.append((SingleRuleGroup(raw_rule_group), user))
            # Default multi rule group is ifelse
            elif raw_rule_group[0][1] == '' \
                    or raw_rule_group[0][1].lower() == 'ifelse': # REFACTOR these enums should live in one spot, we also reference then in RuleGroup.py
                target_list.append((IfElseRuleGroup(raw_rule_group), user))
            elif raw_rule_group[0][1].lower() == 'ifany':
                target_list.append((IfAnyRuleGroup(raw_rule_group), user))
            else:
                self.le('Not processing rule group with type: {}'.format(raw_rule_group[0][1]))
   
    # list of [(RuleGroup, user)...
    def get_rule_groups(self):
        return self.all_rule_groups

    def get_rule_groups_for_user(self, user):
        ret = []
        for rule_group, rule_user in self.all_rule_groups:
            if rule_user == user:
                ret.append(rule_group)
        return ret



