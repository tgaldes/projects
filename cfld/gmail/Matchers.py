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
        if not self.re_string:
            raise Exception('Cannot create {} with empty re_string: {}'.format(self.__class__, self.re_string))
        self.re = re.compile(self.re_string)
        self.ld('Created {}, re_string={}'.format(self.__class__, self.re_string))

    def matches(self, thread):
        if self.re.match(thread.subject()):
            self.ld('SubjectMatcher: \'{}\' matches regex:\'{}\''.format(thread.subject(), self.re_string))
            return True
        return False

    def get_matching_groups(self, thread):
        g = self.re.match(thread.subject())
        if g:
            self.ld('SubjectMatcher: returning groups: {}'.format(g.groups()))
            return g.groups()
        raise Exception('Asked for matching groups when no match. SubjectMatcher re: {} thread subject: {}'.format(self.re_string, thread.subject()))



class ExpressionMatcher(implements(IMatcher), Logger):
    def __init__(self, expression):
        super(ExpressionMatcher, self).__init__(__name__)
        self.expression = expression
        if not self.expression:
            raise Exception('Cannot create {} with empty expression: {}'.format(self.__class__, self.expression))
        self.ld('Created {}, expression={}'.format(self.__class__, self.expression))

    def matches(self, thread):
        return evaluate_expression(self.expression, **locals())

    # Since we aren't doing a regex we don't really have the concept of matching groups
    def get_matching_groups(self, thread):
        return []


class LabelMatcher(implements(IMatcher), Logger):
    def __init__(self, label):
        super(LabelMatcher, self).__init__(__name__)
        self.label = label
        if not self.label:
            raise Exception('Cannot create {} with empty label: {}'.format(self.__class__, self.label))
        self.ld('Created {}, label={}'.format(self.__class__, self.label))
        self.re = re.compile(self.label)

    def matches(self, thread):
        for label in thread.labels():
            if self.re.match(label):
                self.ld('LabelMatcher: \'{}\' matches regex:\'{}\''.format(label, self.label))
                return True
        return False

    def get_matching_groups(self, thread):
        for label in thread.labels():
            g = self.re.match(label)
            if g:
                self.ld('LabelMatcher: returning groups: {}'.format(g.groups()))
                return g.groups()
        raise Exception('Asked for matching groups when no match. LabelMatcher re: {} thread subject: {}'.format(self.label, thread.labels()))
       
class ComboMatcher(implements(IMatcher), Logger):
    def __init__(self, matchers):
        super(ComboMatcher, self).__init__(__name__)
        if len(matchers) == 0:
            raise Exception('Cannot create ComboMatcher with empty list of matchers.')
        self.matchers = matchers
        self.ld('Created {} with {} matchers'.format(self.__class__, len(self.matchers)))

    def matches(self, thread):
        for matcher in self.matchers:
            if not matcher.matches(thread):
                return False
        return True

    def get_matching_groups(self, thread):
        matches = []
        for matcher in self.matchers:
            if matcher.matches(thread):
                matches.extend(list(matcher.get_matching_groups(thread)))
            else: 
                raise Exception('Asked for matching groups when not all match. ComboMatcher with {} sub-matchers'.format(len(self.matchers)))
        return matches
