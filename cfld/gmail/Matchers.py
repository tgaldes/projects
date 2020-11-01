from Interfaces import IMatcher
from interface import implements
import re
import pdb
class SubjectMatcher(implements(IMatcher)):
    def __init__(self, re_string):#, nt):
         
        #self.re_string = 'Lease agreement - (.*) - [0-9A-Za-z]* between .*'#nt.subject_regex
        if not re_string:
            self.re_string = 'test subject'
        else:
            self.re_string = re_string
        self.re = re.compile(self.re_string)

    def matches(self, thread):
        if self.re.match(thread.subject()):
            return True
        return False

    def get_matching_groups(self, thread):
        g = self.re.match(thread.subject())
        if g:
            return g.groups()
        raise Exception('Asked for matching groups when no match. SubjectMatcher re: {} thread subject: {}'.format(self.re_string, thread.subject))


