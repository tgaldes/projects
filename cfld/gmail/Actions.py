from Interfaces import IAction
from interface import implements
from util import evaluate_expression
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
        
