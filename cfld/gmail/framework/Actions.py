import pdb
from interface import implements
import subprocess
import re
from glob import glob

from framework.Interfaces import IAction
from framework.util import evaluate_expression, get_imports
from framework.Thread import Thread
from framework.BaseValidator import BaseValidator
from framework.Logger import Logger
from framework.OpenAiLLM import OpenAiLLM
from framework import constants




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
            self.ld('removing label: {} on thread {}'.format(label_string, thread))
        else:
            self.ld('adding label: {} on thread {}'.format(label_string, thread))
        thread.set_label(label_string, unset=self.unset)

class DestinationBase(Logger):
    def __init__(self, destinations, name):
        super(DestinationBase, self).__init__(name)
        self.destinations = destinations
    def __convert_string_emails_to_list(self, emails):
        if type(emails) == str:
            return emails.split(',')
        return emails
    def _get_destinations(self, thread, matches):
        if self.destinations:
            return self.__convert_string_emails_to_list(evaluate_expression(self.destinations, **locals()))
        else:
            return []

class SendDraftAction(implements(IAction), Logger):
    def __init__(self):
        super(SendDraftAction, self).__init__(__class__)
        self.ld('Created')
    def process(self, thread, matches):
        if thread.has_draft():
            self.li('Sending draft on thread: {}'.format(thread))
            thread.send_draft()
        else:
            self.lw('tried to send a message on a thread without a draft. Thread {}'.format(thread))

class DraftAction(implements(IAction), DestinationBase):
    def __init__(self, value, destinations, prepend=False, name=''):
        if not name:
            super(DraftAction, self).__init__(destinations, __class__)
        else:
            super(DraftAction, self).__init__(destinations, name)
        self.value = value
        self.label_action = LabelAction(constants.add_automation_label)
        self.ld('Created: destinations={}, value={}'.format(self.destinations, self.value))
        self.prepend = prepend
    def process(self, thread, matches):
        self.ld('processing a thread')
        destinations = self._get_destinations(thread, matches)
        if self.value:
            draft_content = evaluate_expression(self.value, **locals())
        else:
            draft_content = ''
        if self.prepend:
            thread.prepend_to_draft(draft_content, destinations)
        else:
            thread.append_to_draft(draft_content, destinations)
        self.label_action.process(thread, matches)

# sk-svcacct-pWzPhMM7a8nRITuGW46H6tqZy4-ClbzJ761p__3_0KXvzDGvotpvHv9w3keMOLOuJ_Uq9T3BlbkFJcJWYt8kc_UEt_r1KX7sFGnHNip7fMFhUk62XgM_Z0tLu2Te7WZ94khA0sjBDn5CEYzUAA
class LLMDraftAction(implements(IAction), DestinationBase):
    def __init__(self, value, destinations, prepend=False, name=''):
        if not name:
            super(LLMDraftAction, self).__init__(destinations, __class__)
        else:
            super(LLMDraftAction, self).__init__(destinations, name)
        self.value = value
        self.label_action = LabelAction(constants.add_automation_label)
        self.ld('Created: destinations={}, value={}'.format(self.destinations, self.value))
        self.prepend = prepend
        self.llm = OpenAiLLM()
    def process(self, thread, matches):
        self.ld('processing a thread')
        destinations = self._get_destinations(thread, matches)
        if self.value:
            draft_content = self.llm.generate_response(thread)
        else:
            draft_content = ''
        if self.prepend:
            thread.prepend_to_draft(draft_content, destinations)
        else:
            thread.append_to_draft(draft_content, destinations)
        self.label_action.process(thread, matches)


# The redirect thread needs to know
# - inbox he'll be sending to
# - how to find the thread he'll be drafting on
# and is created with an action that he will pass the found threads to
class RedirectAction(Logger):
    def __init__(self, inbox, finder_expression, action):
        super(RedirectAction, self).__init__(__class__)
        self.inbox = inbox # set up by factory
        self.thread_finder_expression = finder_expression
        self.action = action
        if not self.thread_finder_expression:
            raise Exception('Cannot create with empty thread_finder_expression: {} '.format(self.thread_finder_expression))
        self.ld('Created: finder_expression={} action={}'.format(self.thread_finder_expression, self.action))
        
    def process(self, thread, matches):
        self.ld('processing a thread')
        found_threads = evaluate_expression(self.thread_finder_expression, **{**locals(), **self.__dict__})
        if not found_threads:
            self.li('No found_threads matched the expression: {}'.format(self.thread_finder_expression))
        for found_thread in found_threads:
            self.action.process(found_thread, matches)

# Like a redirect, but instead of creating a draft in the found thread,
# we'll get the labels from the found thread and set any that match our regex
# in the current thread
class LabelLookupAction(implements(IAction), Logger):
    def __init__(self, inbox, finder_expression, label_regex):
        super(LabelLookupAction, self).__init__(__class__)
        self.inbox = inbox
        self.thread_finder_expression = finder_expression
        self.label_regex_string = label_regex
        self.label_re = re.compile(self.label_regex_string)
        self.ld('Created: thread_finder {} label_regex {}'.format(self.thread_finder_expression, self.label_regex_string))

    def process(self, thread, matches):
        found_threads = evaluate_expression(self.thread_finder_expression, **{**locals(), **self.__dict__})
        if not found_threads:
            self.lw('No found_threads matched the expression: {}'.format(self.thread_finder_expression))
        found = False
        for found_thread in found_threads:
            for label in found_thread.labels():
                if self.label_re.match(label):
                    self.ld('Match label: {} with re: {}'.format(label, self.label_regex_string))
                    thread.set_label(label)
                    found = True
        if not found:
            self.lw('No labels in any found threads matched re: {}'.format(self.label_regex_string))


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
class ForwardAttachmentAction(DestinationBase):
    def __init__(self, destinations):
        super(ForwardAttachmentAction, self).__init__(destinations, __class__)

    def process(self, thread, matches):
        destinations = self._get_destinations(thread, matches)
        last_attachment = thread.last_attachment()
        if len(last_attachment) == 2:
            thread.add_attachment_to_draft(*last_attachment, destinations) 

# We'll do an exec on self.value to get a filename glob, and attach all the matching files
# found on the local drive system
class AttachmentAction(DestinationBase):
    def __init__(self, value, destinations):
        super(AttachmentAction, self).__init__(destinations, __class__)
        self.value = value
        self.ld('Created: file glob expression: {}'.format(self.value))

    def process(self, thread, matches):
        fn_glob = evaluate_expression(self.value, **locals())
        destinations = self._get_destinations(thread, matches)
        for fn in sorted(glob(fn_glob)): # sort for ut behavior
            data = open(fn, 'rb').read()
            self.ld('Adding attachement from file: {}'.format(fn))
            thread.add_attachment_to_draft(data, fn, destinations)
        
class ShellAction(Logger):
    def __init__(self, command):
        super(ShellAction, self).__init__(__class__)
        self.command = command
        self.ld('Created: command={}'.format(self.command))

    def process(self, thread, matches):
        evaluated_command = evaluate_expression(self.command, **locals())
        self.ld('Command evaluated to: {}'.format(evaluated_command))
        if BaseValidator.force_matches:
            return 0
        child = subprocess.Popen(evaluated_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = child.communicate()
        rc = child.returncode

        self.li('stdout: {}'.format(out))
        self.li('stderr: {}'.format(error))

        if rc != 0:
            self.le('subprocess failed.\nstdout: {}\n\nstderr: {}\n\nrc: {}'.format(out, error, rc))
        return rc

