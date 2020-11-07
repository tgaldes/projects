from Matchers import *
from Actions import *
import collections
from Logger import Logger
from RuleHolder import RuleHolder

class RuleFactory(Logger):
    # sheet data is a list of lists
    # first list is the header which we'll use to create a named tuple
    # then for each row we'll create an instance of the desired RuleHolder
    def __init__(self, sheet_data=[], inboxes={}):
        super(RuleFactory, self).__init__(__name__)
        if not sheet_data:
            sheet_data = \
                [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group'], \
                 ['label by school', 'apply', '', '', 'New Submission for (.*)', '', '', 'label', '"Schools/" + matches(0)', '', '', '']]
        RuleTuple = collections.namedtuple('RuleTuple', sheet_data[0])
        self.rule_groups_by_user = {}
        header_size = len(sheet_data[0])
        last_group_index = 0
        for rule_row in sheet_data[1:]:
            log_msg = 'Created: '
            # Google will trim rows when there isn't data in some of the last fields,
            # so insert empty strings here to keep our named tuple happy
            rule_row.extend(['' for x in range(header_size - len(rule_row))])

            tup = RuleTuple(*rule_row)
            if not tup.group or not (int(tup.group) == last_group_index or last_group_index < int(tup.group)):
                self.lw('Cannot specify a group index of {} when last group index was {}'.format(tup.group, last_group_index))
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
                self.lw('Only label regexes, subject regexes, body regexes, and expression matchers are supported for matchers. No rule will be created.')
                continue
            # create action
            if tup.action == 'draft':
                action = DraftAction(tup.value, tup.destinations)
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
            else:
                self.lw('Only draft, label, unlabel, remove_draft, and redirect are supported for actions. No rule will be created for {}.'.format(tup.action))
                continue

            # Create the rule holder
            if len(matchers) == 1:
                rh = RuleHolder(action, matchers[0])
            else:
                rh = RuleHolder(action, ComboMatcher(matchers))

            # Add the RuleHolder
            if tup.email not in self.rule_groups_by_user:
                self.rule_groups_by_user[tup.email] = []
            if int(tup.group) == last_group_index:
                if not self.rule_groups_by_user[tup.email]:
                    self.rule_groups_by_user[tup.email].append([rh]) # Cover the case where first group index is 0
                else:
                    self.rule_groups_by_user[tup.email][-1].append(rh)
            else: # group of one rule
                self.rule_groups_by_user[tup.email].append([rh])
            last_group_index = int(tup.group)

            log_msg += ', Group #{}'.format(tup.group)

            self.li(log_msg)

    def get_rule_groups_for_user(self, user):
        return self.rule_groups_by_user[user]
    
