import pdb
from interface import implements

from Interfaces import IAction
from util import evaluate_expression
from Thread import Thread
from Logger import Logger

class LabelAction(implements(IAction), Logger):
    def __init__(self, value, unset=False):
        super(LabelAction, self).__init__(__name__)
        self.value = value
        self.unset = unset
        self.ld('Created {}, value={}, unset={}'.format(self.__class__, self.value, self.unset))

    def process(self, thread, matches):
        self.ld('{} is processing a thread'.format(self.__class__))
        # use the values we saved in the constructor to run the appropriate code
        label_string = evaluate_expression(self.value, **locals())
        thread.set_label(label_string, unset=self.unset)

class DraftAction(implements(IAction), Logger):
# TODO: add a need human to review label on all drafts we create
    def __init__(self, value, destinations):
        super(DraftAction, self).__init__(__name__)
        self.value = value
        self.destinations = destinations
        self.label_action = LabelAction('automation')
        self.ld('Created {}, destinations={}, value={}'.format(self.__class__, self.destinations, self.value))
    def process(self, thread, matches):
        self.ld('{} is processing a thread'.format(self.__class__))
        draft_content = evaluate_expression(self.value, **locals())
        destinations = evaluate_expression(self.destinations, **locals())
        thread.append_to_draft(draft_content, destinations)
        self.label_action.process()

# There are two differences between a redirect and a draft action
# 1 - the redirect can create a draft on a different thread than the input thread
# 2 - the redirect can create this draft in a different inbox
# The redirect thread needs to know
# - inbox he'll be sending to
# - how to find the thread he'll be drafting on
class RedirectAction(implements(IAction), Logger):
    def __init__(self, inbox, finder_expression, value, destinations):
        super(RedirectAction, self).__init__(__name__)
        self.inbox = inbox # set up by factory
        self.thread_finder_expression = finder_expression
        self.value = value
        self.destinations = destinations
        self.ld('Created {}, destinations={}, value={}, finder_expression={}'.format(self.__class__, self.destinations, self.value, self.finder_expression))
        
    def process(self, thread, matches):
        
        self.ld('{} is processing a thread'.format(self.__class__))
        local_request = 'found_thread = ' + self.thread_finder_expression
        exec(local_request)
        thread = Thread(locals()['found_thread'], self.inbox.get_service())
        # TODO : can call super class here
        draft_content = evaluate_expression(self.value, **locals())
        destinations = evaluate_expression(self.destinations, **locals())
        thread.append_to_draft(draft_content, destinations)


        
