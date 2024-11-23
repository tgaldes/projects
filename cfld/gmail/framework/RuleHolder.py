import pdb
from interface import implements
from framework.Interfaces import IRule
from framework.Logger import Logger

# Holds the classes we create for one row of the sheet
class RuleHolder(Logger, implements(IRule)):
    row_num = 2
    def __init__(self, action, matcher, name='', num = 0):
        super(RuleHolder, self).__init__(__class__)
        self.action = action
        self.matcher = matcher
        if not num:
            self.row_num = RuleHolder.row_num
        else:
            self.row_num = num
        self.name = name
        self.ld('Created #{}: {}'.format(self.row_num, self.name))
        RuleHolder.row_num += 1
    def process(self, thread):
        self.ld('#{}: {}: processing {}'.format(self.row_num, self.name, thread))
        if self.matcher.matches(thread):
            self.ld('#{}: {}: matches'.format(self.row_num, self.name))
            self.action.process(thread)
            return True
        return False


