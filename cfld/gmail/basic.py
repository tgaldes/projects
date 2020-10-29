from interface import Interface, implements


class IAction(Interface):
    def process(self, email):
        pass
class IMatcher(Interface):
    def matches(self, email):
        pass
    def get_matching_groups(self, email):
        pass


import collections
class LabelAction(implements(IAction)):
    def __init__(self, nt):
        # grab and save the appropriate members from the named tuple
        pass
    def process(self, email):
        # use the values we saved in the constructor to run the appropriate code
        pass

import re
class SubjectMatcher(implements(IMatcher)):
    def __init__(self, nt):
        self.re_string = nt.subject_regex
        self.re = re.compile(self.re_string)

    def matches(self, email):
        if self.re.match(email.subject):
            return True
        return False

    def get_matching_groups(self, email):
        g = self.re.match(email.subject):
        if g:
            return g.groups()
        raise Exception('Asked for matching groups when no match. SubjectMatcher re: {} Email subject: {}'.format(self.re_string, email.subject))

