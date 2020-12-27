import collections

from framework.Matchers import *
from framework.Actions import *
from framework.Logger import Logger
from framework.RuleHolder import RuleHolder
from framework.RuleGroup import IfAnyRuleGroup, IfElseRuleGroup, SingleRuleGroup

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
        super(RuleFactory, self).__init__(__class__)
        if len(sheet_data) < 2:
            raise Exception('Tried to construct RuleFactory with data that is only {} row.'.format(len(sheet_data)))
        RuleTuple = collections.namedtuple('RuleTuple', [x.split(' ')[0] for x in sheet_data[0]])
        header_size = len(sheet_data[0])
        last_group_index = -1
        # List of [(Group, user)..... so we can process in order of the rule groups
        raw_rule_group_tuples = []
        count = 1
        for rule_row in sheet_data[1:]:
            count += 1
            if row_is_empty(rule_row):
                continue
            log_msg = 'Created: '
            # Google will trim rows when there isn't data in some of the last fields,
            # so insert empty strings here to keep our named tuple happy
            rule_row.extend(['' for x in range(header_size - len(rule_row))])

            tup = RuleTuple(*rule_row)
            name = tup.name
            if not tup.group or not (float(tup.group) == last_group_index or last_group_index < float(tup.group)):
                raise Exception('Cannot specify a group index of {} when last group index was {}. tup: {}'.format(tup.group, last_group_index, tup))
            if not tup.email:
                raise Exception('Cannot create a rule without a user specified. tup: {}'.format(tup))
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
                    raise Exception('RuleFactory doesn\'t have an inbox configured for dest_email: {}, no rule will be created'.format(tup.dest_email))
                action = RedirectAction(inboxes[tup.dest_email], tup.finder, tup.value, tup.destinations)
                log_msg += 'RedirectAction'
            elif tup.action == 'empty':
                action = EmptyAction()
                log_msg += 'EmptyAction'
            elif tup.action == 'attachment':
                action = AttachmentAction(tup.destinations)
                log_msg += 'AttachmentAction'
            else:
                    print(tup)
                    raise Exception('Only draft, prepend_draft, label, unlabel, remove_draft, and redirect are supported for actions. No rule will be created for {}. tup: {}'.format(tup.action, tup))

            # Create the rule holder
            if len(matchers) == 1:
                rh = RuleHolder(action, matchers[0], name, count)
            else:
                rh = RuleHolder(action, ComboMatcher(matchers), name, count)

            # Add the (RuleHolder, type, rule_type) tuple # TODO
            if float(tup.group) == last_group_index:
                if tup.query:
                    raise Exception('Can only specify a custom query in the first rule of a rule group.')
                raw_rule_group_tuples[-1][0].append((rh, tup.group_type, tup.rule_type))
            else: # group of one rule
                raw_rule_group_tuples.append(([(rh, tup.group_type, tup.rule_type)], tup.email, tup.query))
            last_group_index = float(tup.group)

            log_msg += ', Group #{}'.format(tup.group)

            self.li(log_msg)

        self.all_rule_groups = []
        self.__create_rule_groups(raw_rule_group_tuples, self.all_rule_groups)

    def __create_rule_groups(self, tups, target_list):         
        for raw_rule_group, user, query in tups:
            if not raw_rule_group:
                raise Exception('raw_rule_group of size 0')
            if len(raw_rule_group) == 1:
                target_list.append((SingleRuleGroup(raw_rule_group, query), user))
            # Default multi rule group is ifelse
            elif raw_rule_group[0][1] == '' \
                    or raw_rule_group[0][1].lower() == 'ifelse': # REFACTOR these enums should live in one spot, we also reference then in RuleGroup.py
                target_list.append((IfElseRuleGroup(raw_rule_group, query), user))
            elif raw_rule_group[0][1].lower() == 'ifany':
                target_list.append((IfAnyRuleGroup(raw_rule_group, query), user))
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

    # at the framework level we want to always remove the 'automation' label from
    # any thread that doesn't end with a draft
    def get_rule_groups_for_clean_up(self):
        matcher = LabelMatcher('automation')
        ematcher = ExpressionMatcher('not thread.has_draft()')
        cmatcher = ComboMatcher([matcher, ematcher])
        action = LabelAction('"automation"', unset=True)
        rh = RuleHolder(action, cmatcher)
        rg = SingleRuleGroup([[rh]])
        return rg




