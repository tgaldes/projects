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
        if not self.value:
            raise Exception('Cannot create {} with empty value: {}'.format(self.__class__, self.value))
        self.ld('Created {}, value={}, unset={}'.format(self.__class__, self.value, self.unset))

    def process(self, thread, matches):
        # use the values we saved in the constructor to run the appropriate code
        label_string = evaluate_expression(self.value, **locals())
        if self.unset:
            self.ld('{} removing label: {}'.format(self.__class__, label_string))
        else:
            self.ld('{} adding label: {}'.format(self.__class__, label_string))
        thread.set_label(label_string, unset=self.unset)

# TODO: how to insert link in draft we create?
class DraftAction(implements(IAction), Logger):
    def __init__(self, value, destinations, prepend=False, name=__name__):
        super(DraftAction, self).__init__(name)
        self.value = value
        self.destinations = destinations
        if not self.value or not self.destinations:
            raise Exception('Cannot create {} with empty value: {} or destinations: {}'.format(self.__class__, self.value, self.destinations))
        self.label_action = LabelAction('"automation"')
        self.ld('Created {}, destinations={}, value={}'.format(self.__class__, self.destinations, self.value))
        self.prepend = prepend
    def process(self, thread, matches):
        self.ld('{} is processing a thread'.format(self.__class__))
        draft_content = evaluate_expression(self.value, **locals())
        destinations = evaluate_expression(self.destinations, **locals())
        if self.prepend:
            thread.prepend_to_draft(draft_content, destinations)
        else:
            thread.append_to_draft(draft_content, destinations)
        self.label_action.process(thread, matches)

# There are two differences between a redirect and a draft action
# 1 - the redirect can create a draft on a different thread than the input thread
# 2 - the redirect can create this draft in a different inbox
# The redirect thread needs to know
# - inbox he'll be sending to
# - how to find the thread he'll be drafting on
class RedirectAction(DraftAction):
    def __init__(self, inbox, finder_expression, value, destinations):
        super(RedirectAction, self).__init__(value, destinations, name=__name__, prepend=False)
        self.inbox = inbox # set up by factory
        self.thread_finder_expression = finder_expression
        if  not self.thread_finder_expression:
            raise Exception('Cannot create {} with empty or thread_finder_expression: {} '.format(self.__class__, self.thread_finder_expression))
        self.ld('Created {}, destinations={}, value={}, finder_expression={}'.format(self.__class__, self.destinations, self.value, self.thread_finder_expression))
        
    def process(self, thread, matches):
        self.ld('{} is processing a thread'.format(self.__class__))
        # Careful that the name we do the assignment on in exec doesn't exist in the rest of the current scope
        local_request = 'res = ' + self.thread_finder_expression
        exec(local_request)
        found_threads = locals()['res']
        if not found_threads:
            self.li('No found_threads matched the expression: {}'.format(self.thread_finder_expression))
        for found_thread in found_threads:
            super().process(found_thread, matches)

class RemoveDraftAction(implements(IAction), Logger):
    def __init__(self):
        super(RemoveDraftAction, self).__init__(__name__)
    def process(self, thread, matches):
        self.ld('{} is processing a thread'.format(self.__class__))
        thread.remove_existing_draft()

class EmptyAction(implements(IAction), Logger):
    def __init__(self):
        super(EmptyAction, self).__init__(__name__)
    def process(self, thread, matches):
        pass


        
