from Interfaces import IAction
from interface import implements
from util import evaluate_expression
from Thread import Thread
import pdb

class LabelAction(implements(IAction)):
    def __init__(self, value, unset=False):
        self.value = value
        self.unset = unset

    def process(self, thread, matches):
        # use the values we saved in the constructor to run the appropriate code
        label_string = evaluate_expression(self.value, **locals())
        thread.set_label(label_string, unset=self.unset)

class DraftAction(implements(IAction)):
# TODO: add a need human to review label on all drafts we create
    def __init__(self, value, destinations):
        self.value = value
        self.destinations = destinations
        self.count = 0
    def process(self, thread, matches):
        draft_content = evaluate_expression(self.value, **locals())
        destinations = evaluate_expression(self.destinations, **locals())
        thread.append_to_draft(draft_content, destinations)
        self.count += 1

# There are two differences between a redirect and a draft action
# 1 - the redirect can create a draft on a different thread than the input thread
# 2 - the redirect can create this draft in a different inbox
# The redirect thread needs to know
# - inbox he'll be sending to
# - how to find the thread he'll be drafting on
class RedirectAction(implements(IAction)):
    def __init__(self, inbox, finder_expression, value, destinations):
        self.inbox = inbox # set up by factory
        self.thread_finder_expression = finder_expression
        self.value = value
        self.destinations = destinations
        
    def process(self, thread, matches):
        
        local_request = 'found_thread = ' + self.thread_finder_expression
        exec(local_request)
        thread = Thread(locals()['found_thread'], self.inbox.get_service())
        # TODO : can call super class here
        draft_content = evaluate_expression(self.value, **locals())
        destinations = evaluate_expression(self.destinations, **locals())
        thread.append_to_draft(draft_content, destinations)


        
