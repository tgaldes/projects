import pdb
from interface import implements
from framework.Logger import Logger
from framework.Interfaces import IRule
from framework.util import class_to_string

# Holds the classes we create for one row of the sheet
class RuleHolder(implements(IRule), Logger):
    row_num = 2
    def __init__(self, action, matcher):
        super(RuleHolder, self).__init__(__class__)
        self.action = action
        self.matcher = matcher
        self.row_num = RuleHolder.row_num
        self.ld('Created #{}'.format(RuleHolder.row_num))
        RuleHolder.row_num += 1
    def process(self, thread):
        if self.matcher.matches(thread):
            self.ld('#{} matches'.format(self.row_num))
            match_groups = self.matcher.get_matching_groups(thread)
            self.action.process(thread, match_groups)
            return True
        return False


