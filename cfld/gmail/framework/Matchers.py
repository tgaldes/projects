import re
import pdb
from interface import implements

from framework.Interfaces import IMatcher
from framework.BaseValidator import BaseValidator
from framework.util import evaluate_expression, class_to_string
from framework.Logger import Logger


class RegexMatcher(BaseValidator):
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

    def __clean_text(self, text):
        text = text.replace('\n', '<br>')
        if len(text) > 100:
            return text[:99]
        return text

    def matches(self, text, thread):
        if self.re.match(text):
            self.ld('\'{}\' matches regex:\'{}\' {}'.format(self.__clean_text(text), self.re_string, thread))
            return True
        r = self.__try_non_re_match(text)
        if r:
            self.ld('\'{}\' matches regex:\'{}\' {}'.format(self.__clean_text(text), self.re_string, thread))
            return True
        elif super().force_match():
            # TODO: have a method on thread that will get us what we want the log output to be
            self.ld('\'{}\' forced to return true for {}'.format(self.re_string, thread))
            return True
        else:
            self.ld('\'{}\' no match regex:\'{}\' {}'.format(self.__clean_text(text), self.re_string, thread))
            return False

    def _name(self):
        raise Exception('_name is not implemented in RegexMatcher.')

    def get_matching_groups(self, text):
        g = self.re.match(text)
        if g:
            self.ld('SubjectMatcher: returning groups: {}'.format(g.groups()))
            return g.groups()
        elif self.__try_non_re_match(text):
            return []
        elif super().force_match():
            return []
        raise Exception('Asked for matching groups when no match. re: {} thread subject: {}'.format(self.re_string, text))
    

class SubjectMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, regex):
        super(SubjectMatcher, self).__init__(regex)

    def matches(self, thread):
        return super().matches(thread.subject(), thread)

    def get_matching_groups(self, thread):
        return super().get_matching_groups(thread.subject())

    def _name(self):
        return str(self.__class__)


class BodyMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, re_string):
        super(BodyMatcher, self).__init__(re_string.lower())

    def matches(self, thread):
        return super().matches(thread.last_message_text().lower(), thread)

    def get_matching_groups(self, thread):
        return super().get_matching_groups(thread.last_message_text().lower())

    def _name(self):
        return str(self.__class__)

class LabelMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, re_string):
        super(LabelMatcher, self).__init__(re_string)

    def matches(self, thread):
        for label in thread.labels():
            if super().matches(label, thread):
                return True
        return False

    def get_matching_groups(self, thread):
        for label in thread.labels():
            try:
                return super().get_matching_groups(label)
            except:
                pass
        raise Exception('Asked for matching groups when no matches found for labels: {}'.format(thread.labels()))

    def _name(self):
        return str(self.__class__)


class ExpressionMatcher(BaseValidator, implements(IMatcher)):
    def __init__(self, expression):
        super(ExpressionMatcher, self).__init__(__class__)
        self.expression = expression
        if not self.expression:
            raise Exception('Cannot create {} with empty expression: {}'.format(self.__class__, self.expression))
        self.ld('Created: expression={}'.format(self.expression))

    def matches(self, thread):
        if evaluate_expression(self.expression, **locals()):
            self.ld('{} returns true {}'.format(self.expression, thread))
            return True
        elif super().force_match():
            self.ld('\'{}\' forced to return true for {}'.format(self.expression, thread))
            return True
        self.ld('{} returns false {}'.format(self.expression, thread))
        return False

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
        for i, matcher in enumerate(self.matchers):
            if not matcher.matches(thread):
                self.ld('Returning false when matcher at index {} returns false. {}'.format(i, thread))
                return False
        self.ld('matched {} matchers, returning true for {}'.format(len(self.matchers), thread))
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
        self.li('always returing true for {}'.format(thread))
        return True

    def get_matching_groups(self, thread):
        return []
