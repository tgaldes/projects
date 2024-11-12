import re
import pdb
from interface import implements

from framework.Interfaces import IMatcher
from framework.Logger import Logger
from framework.ContactGroup import ContactGroup


def clean_text(text):
    text = text.replace('\n', '<br>')
    if len(text) > 100:
        return text[:99] + '...'
    return text

class RegexMatcher(Logger):
    def __init__(self, re_string):
        super(RegexMatcher, self).__init__(self._name())
        self.re_string = re_string
        if not self.re_string or self.re_string.isspace():
            raise Exception('Cannot create with empty or whitespace re_string: {}'.format(self.re_string))
        # Force the regexes to match the entire expression
        if self.re_string[0] != '^':
            self.re_string = '^' + self.re_string
        if self.re_string[-1] != '$':
            self.re_string = self.re_string + '$'

        self.re = re.compile(self.re_string)
        self.ld('Created: re_string={}'.format(self.re_string))

    def matches(self, text, thread):
        if self.re.match(text):
            self.ld('\'{}\' matches regex:\'{}\' {}'.format(clean_text(text), self.re_string, thread))
            return True
        else:
            self.ld('\'{}\' no match regex:\'{}\' {}'.format(clean_text(text), self.re_string, thread))
            return False

    def _name(self):
        raise Exception('_name is not implemented in RegexMatcher.')

    def get_matching_groups(self, text):
        g = self.re.match(text)
        if g:
            self.ld('SubjectMatcher: returning groups: {}'.format(g.groups()))
            return g.groups()
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


class BodyMatcher(implements(IMatcher), Logger):

    def __init__(self, needle):
        super(BodyMatcher, self).__init__(__class__)
        self.needle = needle.lower()
        if not self.needle or self.needle.isspace():
            raise Exception('Cannot create BodyMatcher with empty or whitespace needle')

    def matches(self, thread):
        text = thread.last_message_text().lower()
        if self.needle in text:
            self.ld('\'{}\' contains:\'{}\' {}'.format(clean_text(text), self.needle, thread))
            return True
        else:
            self.ld('\'{}\' no match regex:\'{}\' {}'.format(clean_text(text), self.needle, thread))
            return False

    def get_matching_groups(self, thread):
        text = thread.last_message_text().lower()
        if self.needle in text:
            return []
        else:
            raise Exception('Asked for matching groups when no match. needle: {} haystack (trimmed): {}'.format(self.needle, clean_text(text)))
         

class LabelMatcher(implements(IMatcher), RegexMatcher, Logger):

    def __init__(self, re_string, reverse_match=False):
        super(LabelMatcher, self).__init__(re_string)
        self.reverse_match = reverse_match

    def matches(self, thread):
        for label in thread.labels():
            if super().matches(label, thread):
                return not self.reverse_match
        return self.reverse_match

    def get_matching_groups(self, thread):
        for label in thread.labels():
            try:
                return super().get_matching_groups(label)
            except:
                if self.reverse_match:
                    return ()
        raise Exception('Asked for matching groups when no matches found for labels: {}'.format(thread.labels()))

    def _name(self):
        return str(self.__class__)

class ExpressionMatcher(Logger, implements(IMatcher)):
    def __init__(self, expression):
        super(ExpressionMatcher, self).__init__(__class__)
        self.expression = expression
        if not self.expression or self.expression.isspace():
            raise Exception('Cannot create {} with empty or whitespace expression: {}'.format(self.__class__, self.expression))
        self.ld('Created: expression={}'.format(self.expression))

    def matches(self, thread):
        if evaluate_expression(self.expression, **locals()):
            self.ld('{} returns true {}'.format(self.expression, thread))
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
class AllMatcher(Logger):
    def __init__(self):
        super(AllMatcher, self).__init__(__class__)
    
    def matches(self, thread):
        self.li('always returing true for {}'.format(thread))
        return True

    def get_matching_groups(self, thread):
        return []

# return True if any email in the thread is in the group
class ContactGroupMatcher(Logger):
    def __init__(self, group_name):
        super(ContactGroupMatcher, self).__init__(__class__)
        self.group_name = group_name
        self.group = ContactGroup(group_name)
        self.li('Created: group_name={}'.format(self.group_name))

    def matches(self, thread):
        for email in thread.get_thread_emails():
            if self.group.has_email(email):
                self.ld('\'{}\' is in group \'{}\' {}'.format(email, self.group_name, thread))
                return True
        self.ld('No emails from thread in group \'{}\' {}'.format(self.group_name, thread))
        return False

    def get_matching_groups(self, thread):
        return []
