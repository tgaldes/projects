from GMail import g_instance
from interface import Interface, implements
import pdb


# ------------------  globals  ----------------------
def set_label(email, label_string):
    return g_instance.set_label(email, label_string)

def get_short_name(val):
    names = {'2715 Portland Street' : 'USC'} # TODO: read from sheets
    return names[val]

def get_email_subject(email):
    return g_instance.get_subject(email)


# ------------------  end globals  ----------------------

# ----------------- Interfaces -------------------
class IAction(Interface):
    def process(self, email, matches):
        pass
class IMatcher(Interface):
    def matches(self, email):
        pass
    def get_matching_groups(self, email):
        pass

# ----------------- End Interfaces -------------------

# --------------- Interface Implementations -------------------
# TESTING- we can test out our implementations of various rules and matchers
# by importing a different collection of global functions that will work with map based emails instead of the real thing
import collections
class LabelAction(implements(IAction)):
    def __init__(self):#, nt):
        # grab and save the appropriate members from the named tuple
        self.expression = '"Signed leases/" + get_short_name(matches[0])'

    def get_value(self, matches): # TODO: this will go in a base class
        local_request = 'local_result = ' + self.expression
        exec(local_request)
        return locals()['local_result']

    def process(self, email, matches):
        # use the values we saved in the constructor to run the appropriate code
        label_string = self.get_value(matches)
        print(label_string)
        set_label(email, label_string)

import re
class SubjectMatcher(implements(IMatcher)):
    def __init__(self):#, nt):
         
        self.re_string = 'Lease agreement - (.*) - [0-9A-Za-z]* between .*'#nt.subject_regex
        self.re = re.compile(self.re_string)

    def matches(self, email):
        subject = get_email_subject(email)
        if self.re.match(subject):
            return True
        return False

    def get_matching_groups(self, email):
        subject = get_email_subject(email)
        g = self.re.match(subject)
        if g:
            return g.groups()
        raise Exception('Asked for matching groups when no match. SubjectMatcher re: {} Email subject: {}'.format(self.re_string, email.subject))

# --------------- End Interface Implementations -------------------

class RuleHolder:
    def __init__(self, action, matcher):
        self.action = action
        self.matcher = matcher
    def process(self, email):
        if self.matcher.matches(email):
            match_groups = self.matcher.get_matching_groups(email)
            self.action.process(email, match_groups)

if __name__=='__main__':
    action = LabelAction()
    matcher = SubjectMatcher()
    rule_holder = RuleHolder(action, matcher)
    email = g_instance.get_one_email()
    rule_holder.process(email)
