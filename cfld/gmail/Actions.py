from Interfaces import IAction
from interface import implements
from util import evaluate_expression
from Thread import Thread
import pdb

class LabelAction(implements(IAction)):
    def __init__(self, value):
        self.value = value

    def process(self, thread, matches):
        # use the values we saved in the constructor to run the appropriate code
        label_string = evaluate_expression(self.value, **locals())
        thread.set_label(label_string)

class DraftAction(implements(IAction)):
    def __init__(self):
        self.value = '"this is a draft message saying whatever it is that we want to say"'
        self.destinations = 'kwargs["thread"].default_reply()' # TODO: figure out a wrapper like match()
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
    def __init__(self, inbox):
        self.inbox = inbox # set up by factory
        self.thread_finder_expression = 'self.inbox.get_threads_from_email_address(thread.get_new_application_email())'
        self.value = '"{}, we got your app and processed it, you\'ll need to approve it on your end so we can get your background and credit score.".format(thread.salutation())'
        self.destinations = 'thread.default_reply()'
        
    def process(self, thread, matches):
        
        local_request = 'found_thread = ' + self.thread_finder_expression
        exec(local_request)
        thread = Thread(locals()['found_thread'], self.inbox.get_service())
        # TODO : can call super class here
        draft_content = evaluate_expression(self.value, **locals())
        destinations = evaluate_expression(self.destinations, **locals())
        thread.append_to_draft(draft_content, destinations)


        
