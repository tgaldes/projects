
class RuleHolder:
    def __init__(self, action, matcher):
        self.action = action
        self.matcher = matcher
    def process(self, thread):
        if self.matcher.matches(thread):
            match_groups = self.matcher.get_matching_groups(thread)
            self.action.process(thread, match_groups)


