from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64
from email import encoders
import pdb

from util import list_of_emails_to_string_of_emails


class Thread:
    def __init__(self, thread, service):
        self.service = service
        self.thread = thread

    def subject(self):
        return self.field('Subject')
    
    def field(self, field_name):
# handle a thread
        if field_name in self.thread:
            return self.thread[field_name]
        message = self.thread
        if 'payload' not in self.thread or 'headers' not in self.thread['payload']:
            message = self.thread['messages'][0]
        header = message['payload']['headers']
        for m in header:
            if m['name'] == field_name:
                return m['value']

    def set_label(self, label_string):
        label_id = self.service.get_label_id(label_string)
        if label_id:
            payload = { 'addLabelIds' : [label_id],
                        'removeLabelIds' : []
                      }
            self.service.set_label(self.thread['id'], payload)
        else:
            pass # TODO: create label on demand
        # TODO: update state of thread instance

    def default_reply(self): # TODO: reply all? # TODO: test getting the reply when we aren't replying to the first email in the thread
        return self.field('From').split(' ')[-1].strip('<').strip('>')

    def existing_draft_text(self):
        if 'labelIds' in self.thread['messages'][-1] and 'DRAFT' in self.thread['messages'][-1]['labelIds']:
            return self.thread['messages'][-1]['snippet'] + '\n\n' # TODO: who should be adding the newlines?
        return ''

    def existing_draft_id(self):
        if 'labelIds' in self.thread['messages'][-1] and 'DRAFT' in self.thread['messages'][-1]['labelIds']:
# We finish with a draft message, now get the DRAFT ID (which is different than a message id)
            for draft in self.service.get_drafts():
                if draft['message']['id'] == self.thread['messages'][-1]['id']:
                    return draft['id']
        return None

    def append_to_draft(self, body, destinations):
# TODO: what if destinations != existing draft destinations? maybe we should map the existing draft by who they are being sent to
        message = MIMEText(self.existing_draft_text() + body)
        draft_id = self.existing_draft_id()

        message['to'] = list_of_emails_to_string_of_emails(destinations)
        message['from'] = 'tyler@cleanfloorslockingdoors.com'
        message['subject'] = self.field('Subject')
        message['In-Reply-To'] = self.field('Message-ID')
        message['References'] = self.field('Message-ID')# + ',' + self.get('References')
        payload = {'message' : {'threadId' : self.thread['id'], 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
        self.service.append_or_create_draft(payload, draft_id)
# TODO: update internal state if new draft

        
