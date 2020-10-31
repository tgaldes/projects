from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64
from email import encoders
import pdb

from util import list_of_emails_to_string_of_emails, update_thread


# Once I get the mapping down I need to write 20 asserts for the thread class before adding more functionality
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
            resp = self.service.set_label(self.thread['id'], payload) # TODO: test we update our state after label call
            update_thread(self.thread, resp)
        else:
            pass # TODO: create label on demand

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
    def add_or_update_message(self, message):
        for i, old_message in enumerate(self.thread['messages']):
            if old_message['id'] == message['id']:
                self.thread['messages'][i] = message
                return
        self.thread['messages'].append(message)
                
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
        message = self.service.append_or_create_draft(payload, draft_id)
        self.add_or_update_message(message) # TODO: test that we update or add the message


    # Get the greeting we want to use for messages sent to the thread
    # If we are sending to multiple people, something like 'Hi all,\n\n'
    # For one person, 'Hi first_name,\n\n'
    # The form submitted through the website will make it easy to find their first name 
    # We would need to implement for each Zillow/RentPath/Zumper auto reach out
    # Once we have a message sent by us, we can grab the first line of the email and use that
    def salutation(self):
        pass
    # Return true if we want to send a follow up email to the thread confirming that the 
    # tenant is no longer interested in housing
    # Conditions- last message was sent by userId='me' more than duration_days ago
    def make_them_say_no(self, duration_days=5):
        pass

    # return a dictionary of all the fields in the New Submission for short_name message
    # dictionary will look like {'name' : 'Tony K', 'email' : 'tony@ucla.edu' .....}
    # return {} when this is not a New Submission thread
    def parse_new_submission(self):
        pass

    def get_email_from_new_submission(self): # TODO: maybe we leave looking in the dictionary to the caller of the above func
        pass
        
    def default_reply(self): # TODO: reply all? # TODO: test getting the reply when we aren't replying to the first email in the thread
        return [self.field('From').split(' ')[-1].strip('<').strip('>')]

    # Return a list of all the people in the from, to, and cc fields
    # Filter out the email of userId='me'
    def reply_all(self):
        pass

