import re
import pdb

from Interfaces import IMatcher
from interface import implements
from Logger import Logger
from util import evaluate_expression
class SubjectMatcher(implements(IMatcher), Logger):
    def __init__(self, re_string):
        super(SubjectMatcher, self).__init__(__name__)
        self.re_string = re_string
        self.re = re.compile(self.re_string)

    def matches(self, thread):
        if self.re.match(thread.subject()):
            self.li('SubjectMatcher: \'{}\' matches regex:\'{}\''.format(thread.subject(), self.re_string))
            return True
        return False

    def get_matching_groups(self, thread):
        g = self.re.match(thread.subject())
        if g:
            self.li('SubjectMatcher: returning groups: {}'.format(g.groups()))
            return g.groups()
        raise Exception('Asked for matching groups when no match. SubjectMatcher re: {} thread subject: {}'.format(self.re_string, thread.subject))

class ExpressionMatcher(implements(IMatcher), Logger):
    def __init__(self, expression):
        super(ExpressionMatcher, self).__init__(__name__)
        self.expression = expression

    def matches(self, thread):
        return evaluate_expression(self.expression, **locals())

    # Since we aren't doing a regex we don't really have the concept of matching groups
    def get_matching_groups(self, thread):
        return []
