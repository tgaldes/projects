import pdb
from interface import implements

from framework.Interfaces import IAction
from framework.util import evaluate_expression, get_imports
from framework.Thread import Thread
from framework.Logger import Logger

class LabelAction(implements(IAction), Logger):
    def __init__(self, value, unset=False):
        super(LabelAction, self).__init__(__class__)
        self.value = value
        self.unset = unset
        if not self.value:
            raise Exception('Cannot create with empty value: {}'.format(self.value))
        self.ld('Created: value={}, unset={}'.format(self.value, self.unset))

    def process(self, thread, matches):
        # use the values we saved in the constructor to run the appropriate code
        label_string = evaluate_expression(self.value, **locals())
        if self.unset:
            self.ld('removing label: {}'.format(label_string))
        else:
            self.ld('adding label: {}'.format(label_string))
        thread.set_label(label_string, unset=self.unset)

class DraftAction(implements(IAction), Logger):
    def __init__(self, value, destinations, prepend=False, name=''):
        if not name:
            super(DraftAction, self).__init__(__class__)
        else:
            super(DraftAction, self).__init__(name)
        self.value = value
        self.destinations = destinations
        self.label_action = LabelAction('"automation"')
        self.ld('Created: destinations={}, value={}'.format(self.destinations, self.value))
        self.prepend = prepend
    def process(self, thread, matches):
        self.ld('processing a thread')
        if self.value:
            draft_content = evaluate_expression(self.value, **locals())
        else:
            draft_content = ''
        def convert_string_emails_to_list(emails):
            if type(emails) == str:
                return emails.split(',')
            return emails
        if self.destinations:
            destinations = convert_string_emails_to_list(evaluate_expression(self.destinations, **locals()))
        else:
            destinations = []
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
        super(RedirectAction, self).__init__(value, destinations, name=__class__, prepend=False)
        self.inbox = inbox # set up by factory
        self.thread_finder_expression = finder_expression
        if  not self.thread_finder_expression:
            raise Exception('Cannot create with empty or thread_finder_expression: {} '.format(self.thread_finder_expression))
        self.ld('Created: destinations={}, value={}, finder_expression={}'.format(self.destinations, self.value, self.thread_finder_expression))
        
    def process(self, thread, matches):
        self.ld('processing a thread')
        # Careful that the name we do the assignment on in exec doesn't exist in the rest of the current scope
        # TODO: why don't we use the util.evaluate_expression function? because we use self, so going forward it would be valuable to expose instance vars to util.evaluate_expression
        local_request = get_imports() +'res = ' + self.thread_finder_expression
        exec(local_request)
        found_threads = locals()['res']
        if not found_threads:
            self.li('No found_threads matched the expression: {}'.format(self.thread_finder_expression))
        for found_thread in found_threads:
            super().process(found_thread, matches)

class RemoveDraftAction(implements(IAction), Logger):
    def __init__(self):
        super(RemoveDraftAction, self).__init__(__class__)
    def process(self, thread, matches):
        self.ld('processing a thread')
        thread.remove_existing_draft()

class EmptyAction(implements(IAction), Logger):
    def __init__(self):
        super(EmptyAction, self).__init__(__class__)
    def process(self, thread, matches):
        pass

# Create a draft to the destinations in the same thread, grabbing all attachments
# and content from the most recent message in the thread
class AttachmentAction(Logger):
    def __init__(self, destinations):
        super(AttachmentAction, self).__init__(__class__)
        self.destinations = destinations

    def process(self, thread, matches):
        destinations = evaluate_expression(self.destinations, **locals())
        thread.add_attachment_to_draft(*thread.last_attachment(), destinations) 
        



        
