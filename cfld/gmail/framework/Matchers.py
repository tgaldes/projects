import re
import pdb
from interface import implements

from framework.Interfaces import IMatcher
from framework.Logger import Logger
from framework.util import evaluate_expression, class_to_string


class RegexMatcher(Logger):
    def __init__(self, re_string):
        super(RegexMatcher, self).__init__(self._name())
        self.re_string = re_string
        if not self.re_string:
            raise Exception('Cannot create with empty re_string: {}'.format(self.re_string))
        self.re = re.compile(self.re_string)
        self.ld('Created: re_string={}'.format(self.re_string))

    # re struggles with really large haystacks and greedy matching
    # since the BodyMatcher will be using a lot of .*text.* regexes
    # and won't usually care about groups, we can use a simpler method
    def __try_non_re_match(self, text): # TODO: ut
        trimmed_re_string = self.re_string
        if self.re_string[:2] == '.*':
            trimmed_re_string = trimmed_re_string[2:]
        if self.re_string[-2:] == '.*':
            trimmed_re_string = trimmed_re_string[:-2]

        if text.find(trimmed_re_string) >= 0:
            return True
        return False

    def matches(self, text):
        if self.re.match(text):
            self.ld('\'{}\' matches regex:\'{}\''.format(text, self.re_string))
            return True
        return self.__try_non_re_match(text)

    def _name(self):
        raise Exception('_name is not implemented in RegexMatcher.')

    def get_matching_groups(self, text):
        g = self.re.match(text)
        if g:
            self.ld('SubjectMatcher: returning groups: {}'.format(g.groups()))
            return g.groups()
        elif self.__try_non_re_match(text):
            return ()
        raise Exception('Asked for matching groups when no match. re: {} thread subject: {}'.format(self.re_string, text))
    

class SubjectMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, regex):
        super(SubjectMatcher, self).__init__(regex)

    def matches(self, thread):
        return super().matches(thread.subject())

    def get_matching_groups(self, thread):
        return super().get_matching_groups(thread.subject())

    def _name(self):
        return str(self.__class__)


class BodyMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, re_string):
        super(BodyMatcher, self).__init__(re_string.lower())

    def matches(self, thread):
        return super().matches(thread.last_message_text().lower())

    def get_matching_groups(self, thread):
        return super().get_matching_groups(thread.last_message_text().lower())

    def _name(self):
        return str(self.__class__)

class LabelMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, re_string):
        super(LabelMatcher, self).__init__(re_string)

    def matches(self, thread):
        for label in thread.labels():
            if super().matches(label):
                return True
        return False

    def get_matching_groups(self, thread):
        for label in thread.labels():
            if super().matches(label):
                return super().get_matching_groups(label)
        raise Exception('Asked for matching groups when no matches found for labels: {}'.format(thread.labels()))

    def _name(self):
        return str(self.__class__)


class ExpressionMatcher(implements(IMatcher), Logger):
    def __init__(self, expression):
        super(ExpressionMatcher, self).__init__(__class__)
        self.expression = expression
        if not self.expression:
            raise Exception('Cannot create {} with empty expression: {}'.format(self.__class__, self.expression))
        self.ld('Created: expression={}'.format(self.expression))

    def matches(self, thread):
        return evaluate_expression(self.expression, **locals())

    # Since we aren't doing a regex we don't really have the concept of matching groups
    def get_matching_groups(self, thread):
        return []


# AND behavior (later we can make it and/or)
class ComboMatcher(implements(IMatcher), Logger):
    def __init__(self, matchers):
        super(ComboMatcher, self).__init__(__class__)
        if len(matchers) == 0:
            raise Exception('Cannot create ComboMatcher with empty list of matchers.')
        self.matchers = matchers
        self.ld('Created: with {} matchers'.format(len(self.matchers)))

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

# Always match the thread! Created to use as the matcher for the any rules
# in the IfAnyRuleGroup, that way we don't have to specify .* for one of our
# regex matchers for all of these rules
class AllMatcher(Logger): # TODO ut
    def __init__(self):
        super(AllMatcher, self).__init__(__class__)
    
    def matches(self, thread):
        return True

    def get_matching_groups(self, thread):
        return ()
