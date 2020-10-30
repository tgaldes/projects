from Interfaces import IAction
from interface import implements
from util import evaluate_expression, get_short_name
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
        self.value = '"this is an additional test draft message"'
        self.destinations = '[kwargs["thread"].default_reply()]'
        self.count = 0
    def process(self, thread, matches):
        draft_content = evaluate_expression(self.value, **locals()) + ' ' + str(self.count)
        destinations = evaluate_expression(self.destinations, **locals())
        thread.append_to_draft(draft_content, destinations)
        self.count += 1

