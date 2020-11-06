from Logger import Logger

class RuleHolder(Logger):
    count = 0
    def __init__(self, action, matcher):
        super(RuleHolder, self).__init__(__name__)
        self.action = action
        self.matcher = matcher
        self.count = RuleHolder.count
        self.ld('Created {} #{}'.format(self.__class__, RuleHolder.count))
        RuleHolder.count += 1
    def process(self, thread):
        if self.matcher.matches(thread):
            self.ld('{} #{} matches'.format(self.__class__, self.count))
            match_groups = self.matcher.get_matching_groups(thread)
            self.action.process(thread, match_groups)


