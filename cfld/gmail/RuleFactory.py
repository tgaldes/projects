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
                [['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations'], \
                 ['label by school', 'apply', '', '', 'New Submission for (.*)', '', '', 'label', '"Schools/" + matches(0)', '', '']]
        RuleTuple = collections.namedtuple('RuleTuple', sheet_data[0])
        self.rules_by_user = {}
        header_size = len(sheet_data[0])
        for rule_row in sheet_data[1:]:
            log_msg = 'Created: '
            # Google will trim rows when there isn't data in some of the last fields,
            # so insert empty strings here to keep our named tuple happy
            rule_row.extend(['' for x in range(header_size - len(rule_row))])

            tup = RuleTuple(*rule_row)
            matchers = []
            # create matcher
            if tup.subject_regex:
                matchers.append(SubjectMatcher(tup.subject_regex))
                log_msg += 'SubjectMatcher, '
            if tup.expression_match:
                matchers.append(ExpressionMatcher(tup.expression_match))
                log_msg += 'ExpressionMatcher, '
            if tup.label_regex:
                matchers.append(LabelMatcher(tup.label_regex))
                log_msg += 'LabelMatcher, '
            if not matchers:
                self.lw('Only subject regexes, label regexes, and expression matchers are supported for matchers. No rule will be created.')
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
            elif tup.action == 'redirect':
                if tup.dest_email not in inboxes:
                    self.lw('RuleFactory doesn\'t have an inbox configured for dest_email: {}, no rule will be created'.format(tup.dest_email))
                    continue
                action = RedirectAction(inboxes[tup.dest_email], tup.finder, tup.value, tup.destinations)
                log_msg += 'RedirectAction'
            else:
                self.lw('Only draft, label, and redirects are supported for actions. No rule will be created for {}.'.format(tup.action))
                continue

            if tup.email not in self.rules_by_user:
                self.rules_by_user[tup.email] = []
            if len(matchers) == 1:
                self.rules_by_user[tup.email].append(RuleHolder(action, matchers[0]))
            else:
                self.rules_by_user[tup.email].append(RuleHolder(action, ComboMatcher(matchers)))

            self.li(log_msg)

    def get_rules_for_user(self, user):
        return self.rules_by_user[user]
    
