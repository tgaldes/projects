import collections

from framework.Matchers import *
from framework.Actions import *
from framework.Logger import Logger
from framework.RuleHolder import RuleHolder
from framework.RuleGroup import IfAnyRuleGroup, IfElseRuleGroup, SingleRuleGroup
from framework.Config import Config

def row_is_empty(row):
    for item in row:
        if item:
            return False
    return True

class RuleFactory(Logger):
    # sheet data is a list of lists
    # first list is the header which we'll use to create a named tuple
    # then for each row we'll create an instance of the desired RuleHolder

    # support **kwargs, right now we'll have llm_data and action_data
    def __init__(self, sheet_data=[], inboxes={}, **kwargs):
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
            # create one or more matchers
            if getattr(tup, 'label_regex', None):
                matchers.append(LabelMatcher(tup.label_regex))
                log_msg += 'LabelMatcher, '
            if getattr(tup, 'subject_regex', None):
                matchers.append(SubjectMatcher(tup.subject_regex))
                log_msg += 'SubjectMatcher, '
            if getattr(tup, 'body_regex', None):
                matchers.append(BodyMatcher(tup.body_regex))
                log_msg += 'BodyMatcher, '
            if getattr(tup, 'expression_match', None):
                matchers.append(ExpressionMatcher(tup.expression_match))
                log_msg += 'ExpressionMatcher, '
            # check if contact group match is specified
            if getattr(tup, 'contact_group_match', None):
                matchers.append(ContactGroupMatcher(tup.contact_group_match))
                log_msg += 'ContactGroupMatcher, '
            # framework level behavior to never to never match with a draft action when
            # the 'automation/force_skip' label is present. This is implemented so that
            # the framework doesn't delete or modify a draft that the user might be 
            # actively working on in the web client.
            if getattr(tup, 'action', None) in ['draft', 'prepend_draft', 'forward_attachment', 'attachment', 'remove_draft', 'llm_draft', 'llm_find_text']:
                matchers.append(LabelMatcher(Config().get_force_skip_label(), reverse_match=True))
            if not matchers:
                matchers.append(AllMatcher())
                log_msg += 'AllMatcher, '
            # create action
            supported_actions = ['draft', 'prepend_draft', 'label', 'unlabel', 'remove_draft', 'redirect/redirect_draft', 'redirect_label', 'empty/\'\'', 'forward_attachment', 'attachment', 'label_lookup', 'shell', 'send_draft', 'browser_use']
            if tup.action == 'draft':
                action = DraftAction(tup.value, tup.destinations)
                log_msg += 'DraftAction'
            elif tup.action == 'llm_draft':
                action = LLMDraftAction(tup.value, tup.destinations, kwargs['llm_data'])
                log_msg += 'LLMDraftAction'
            elif tup.action == 'llm_find_text':
                action = LLMFindTextAction(tup.value, tup.destinations, kwargs['llm_data'])
                log_msg += 'LLMFindTextAction'
            elif tup.action == 'llm_label':
                action = LLMLabelAction(tup.value, kwargs['llm_data'])
                log_msg += 'LLMLabelAction'
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
            elif tup.action == 'shell':
                raise Exception('Shell action is not supported. It was deprecated to simplify the value column for browser use.')
                #action = ShellAction(tup.value, kwargs['action_data'])
                #log_msg += 'ShellAction'
            elif tup.action == 'browser_use':
                action = BrowserUseAction(tup.value, kwargs['action_data'])
                log_msg += 'BrowserUseAction'
            elif tup.action == 'redirect_draft' or tup.action == 'redirect':
                if tup.dest_email not in inboxes:
                    raise Exception('RuleFactory doesn\'t have an inbox configured for dest_email: {}, no rule will be created'.format(tup.dest_email))
                inner_action = DraftAction(tup.value, tup.destinations)
                action = RedirectAction(inboxes[tup.dest_email], tup.finder, inner_action)
                log_msg += 'RedirectDraftAction'
            elif tup.action == 'redirect_label':
                if tup.dest_email not in inboxes:
                    raise Exception('RuleFactory doesn\'t have an inbox configured for dest_email: {}, no rule will be created'.format(tup.dest_email))
                inner_action = LabelAction(tup.value)
                action = RedirectAction(inboxes[tup.dest_email], tup.finder, inner_action)
                log_msg += 'RedirectLabelAction'
            elif tup.action == 'empty' or not tup.action:
                action = EmptyAction()
                log_msg += 'EmptyAction'
            # grabs attachment from email thread
            elif tup.action == 'forward_attachment':
                action = ForwardAttachmentAction(tup.destinations)
                log_msg += 'ForwardAttachmentAction'
            # Looks for files on computer
            elif tup.action == 'attachment':
                action = AttachmentAction(tup.value, tup.destinations)
                log_msg += 'AttachmentAction'
            elif tup.action == 'label_lookup':
                if tup.dest_email not in inboxes:
                    raise Exception('RuleFactory doesn\'t have an inbox configured for dest_email: {}, no rule will be created'.format(tup.dest_email))
                action = LabelLookupAction(inboxes[tup.dest_email], tup.finder, tup.value)
                log_msg += 'LabelLookupAction'
            elif tup.action == 'shell':
                action = ShellAction(tup.value)
                log_msg += 'ShellAction'
            elif tup.action == 'send_draft':
                action = SendDraftAction()
            else:
                    print(tup)
                    raise Exception('Supported actions are: {} No rule will be created for {}. tup: {}'.format(supported_actions, tup.action, tup))

            # Create the rule holder
            if len(matchers) == 1:
                rh = RuleHolder(action, matchers[0], name, count)
            else:
                rh = RuleHolder(action, ComboMatcher(matchers), name, count)

            # Add the (RuleHolder, type, rule_type) tuple # TODO
            if float(tup.group) == last_group_index:
                if tup.query:
                    raise Exception('Can only specify a custom query in the first rule of a rule group.')
                raw_rule_group_tuples[-1][0].append([rh, tup.group_type, tup.rule_type])
            else: # group of one rule
                raw_rule_group_tuples.append([[(rh, tup.group_type, tup.rule_type)], tup.email, tup.query])
            last_group_index = float(tup.group)

            log_msg += ', Group #{}'.format(tup.group)

            self.li(log_msg)

        self.all_rule_groups = [[], [], []]
        self.__create_rule_groups(raw_rule_group_tuples, self.all_rule_groups)

    # target_lists [0] == normal, [1], preprocess, [2] post process
    def __create_rule_groups(self, tups, target_lists):         
        for raw_rule_group, user, query in tups:
            index = 0
            if 'pre' in raw_rule_group[0][1].lower():
                index = 1
                self.ld('Creating pre process rule group')
            elif 'post' in raw_rule_group[0][1].lower():
                index = 2
                self.ld('Creating post process rule group')
            if not raw_rule_group:
                raise Exception('raw_rule_group of size 0')
            rule_type_name = raw_rule_group[0][1].lower().replace('pre', '').replace('post', '')
            if len(raw_rule_group) == 1:
                target_lists[index].append(SingleRuleGroup(raw_rule_group, query, user))
            # Default multi rule group is ifelse
            elif rule_type_name == '' \
                    or rule_type_name == 'ifelse': # REFACTOR these enums should live in one spot, we also reference then in RuleGroup.py
                target_lists[index].append(IfElseRuleGroup(raw_rule_group, query, user))
            elif rule_type_name == 'ifany':
                target_lists[index].append(IfAnyRuleGroup(raw_rule_group, query, user))
            else:
                self.le('Not processing rule group with type: {}'.format(raw_rule_group[0][1]))
   
    # list of [RuleGroup, ...
    def get_rule_groups(self):
        return self.all_rule_groups[0]

    def get_pre_process_rule_groups(self, user):
        return self.__get_pre_post(user, 1)
    def get_post_process_rule_groups(self, user):
        return self.__get_pre_post(user, 2)
    def __get_pre_post(self, user, index):
        ret = []
        for rule in self.all_rule_groups[index]:
            if rule.get_user() == user:
                ret.append(rule)
        return ret




