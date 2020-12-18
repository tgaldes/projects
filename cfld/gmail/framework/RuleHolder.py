import pdb
from interface import implements
from framework.Logger import Logger
from framework.Interfaces import IRule

class RuleHolder(implements(IRule), Logger):
    row_num = 2
    def __init__(self, action, matcher):
        super(RuleHolder, self).__init__(__name__)
        self.action = action
        self.matcher = matcher
        self.row_num = RuleHolder.row_num
        self.ld('Created {} #{}'.format(self.__class__, RuleHolder.row_num))
        RuleHolder.row_num += 1
    def process(self, thread):
        if self.matcher.matches(thread):
            self.ld('{} #{} matches'.format(self.__class__, self.row_num))
            match_groups = self.matcher.get_matching_groups(thread)
            self.action.process(thread, match_groups)
            return True
        return False


