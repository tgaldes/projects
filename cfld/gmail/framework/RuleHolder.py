import pdb
from interface import implements
from framework.Interfaces import IRule
from framework.util import class_to_string
from framework.BaseValidator import BaseValidator

# Holds the classes we create for one row of the sheet
class RuleHolder(BaseValidator, implements(IRule)):
    row_num = 2
    def __init__(self, action, matcher, num = 0):
        super(RuleHolder, self).__init__(__class__)
        self.action = action
        self.matcher = matcher
        if not num:
            self.row_num = RuleHolder.row_num
        else:
            self.row_num = num
        self.ld('Created #{}'.format(RuleHolder.row_num))
        RuleHolder.row_num += 1
    def process(self, thread):
        if self.matcher.matches(thread) or super().force_match():
            self.ld('#{} matches'.format(self.row_num))
            match_groups = self.matcher.get_matching_groups(thread)
            self.action.process(thread, match_groups)
            return True
        return False


