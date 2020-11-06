from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64
from email import encoders
import pdb
from time import time

from util import list_of_emails_to_string_of_emails, update_thread
from Logger import Logger
import base64

domains = ['cleanfloorslockingdoors.com', 'cf-ld.com']
# Once I get the mapping down I need to write 20 asserts for the thread class before adding more functionality
class Thread(Logger):
    def __init__(self, thread, service):
        super(Thread, self).__init__(__name__)
        self.service = service
        self.thread = thread
        self.li('Initialized thread with id: {} subject: {}'.format(self.field('id'), self.subject()))

    def subject(self):
        return self.field('Subject')
    
    def field(self, field_name, subset={}, default=None):
        search_dict = self.thread
        if subset:
            search_dict = subset
        if not search_dict:
            return default
# handle a thread
        if field_name in search_dict:
            return search_dict[field_name]
        message = search_dict
        if 'payload' not in search_dict or 'headers' not in search_dict['payload']:
            if 'messages' not in search_dict:
                return default
            message = search_dict['messages'][0]
        if field_name in message:
            return message[field_name]
        header = message['payload']['headers']
        for m in header:
            if m['name'] == field_name:
                return m['value']
        return default

    def set_label(self, label_string, unset=False):
        label_id = self.service.get_label_id(label_string)
        if label_id:
            payload = { 'addLabelIds' : [],
                        'removeLabelIds' : []
                      }
            if unset:
                payload['removeLabelIds'] = [label_id]
            else:
                payload['addLabelIds'] = [label_id]
            resp = self.service.set_label(self.thread['id'], payload)
            update_thread(self.thread, resp)
        else:
            raise Exception('Service cannot find a label id for label: {}'.format(label_string))

    def labels(self):
        message = self.thread['messages'][0]
        labels = []
        for labelid in message['labelIds']:
            labels.append(self.service.get_label_name(labelid))

        return labels

    def append_to_draft(self, body, destinations):
        self.__check_destinations_match(destinations)
        new_body = self.existing_draft_text() + body
        self.ld('New draft will have body: {}'.format(new_body))
        message = MIMEText(new_body)
        draft_id = self.existing_draft_id()

        message['to'] = list_of_emails_to_string_of_emails(destinations)
        message['from'] = self.service.get_email()
        message['subject'] = self.field('Subject')
        message['In-Reply-To'] = self.field('Message-ID', subset=self.__last_message())
        message['References'] = self.field('Message-ID', subset=self.__last_message())
        payload = {'message' : {'threadId' : self.thread['id'], 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
        message = self.service.append_or_create_draft(payload, draft_id)
        self.__add_or_update_message(message)

    # Get the greeting we want to use for messages sent to the thread
    # If we are sending to multiple people, something like 'Hi all,\n\n'
    # For one person, 'Hi first_name,\n\n'
    # The form submitted through the website will make it easy to find their first name 
    # We would need to implement for each Zillow/RentPath/Zumper auto reach out
    # Once we have a message sent by us, we can grab the first line of the email and use that
    def salutation(self):
        return 'Hi this method is not implemented'
        pass

    # Return true if we want to send a follow up email to the thread confirming that the 
    # tenant is no longer interested in housing
    # Conditions- last message was sent by userId='me' more than duration_days ago
    def need_make_them_say_no(self, duration_days=2, time_getter_f=time):
        ts_true = self.last_ts() + duration_days * 86400 < time_getter_f()
        # last message is from userId=me 
        # AND we have sent that message (as opposed to a draft)
        last_msg_true = \
            self.__is_my_email(self.__extract_email(self.field('From', subset=self.__last_message()))) \
            and 'labelIds' in self.thread['messages'][-1] \
            and 'SENT' in self.thread['messages'][-1]['labelIds']
        return ts_true and last_msg_true

    # return a dictionary of all the fields in the New Submission for short_name message
    # dictionary will look like {'name' : 'Tony K', 'email' : 'tony@ucla.edu' .....}
    # return {} when this is not a New Submission thread
    def parse_new_submission(self):
        pass

    def get_email_from_new_submission(self): # TODO: maybe we leave looking in the dictionary to the caller of the above func
        pass
        
    # For reply all, get everything in the from, to, and cc fields that isn't our email
    def default_reply(self, reply_all=True):
        counter = -1
        while True:
            message = self.thread['messages'][counter]
            counter -= 1
            if 'DRAFT' in message['labelIds']:
                continue
            emails = []
            from_email = self.__extract_email(self.field('From', subset=message))
            if not self.__is_my_email(from_email):
                emails.append(from_email)
            to_emails = self.field('To', subset=message).split(',')
            for i, to_email in enumerate(to_emails):
                to_emails[i] = self.__extract_email(to_email)
                if not self.__is_my_email(to_emails[i]):
                    emails.append(to_emails[i])
            if reply_all:
                cc_emails = self.field('Cc', subset=message)
                if cc_emails: # Not every message has cc field
                    cc_emails = cc_emails.split(',')
                    for i, cc_email in enumerate(cc_emails):
                        cc_emails[i] = self.__extract_email(cc_email)
                        if not self.__is_my_email(cc_emails[i]):
                            emails.append(cc_emails[i])
            return emails

                
        raise Exception('Couldn\'t find email that didn\'t match our own')

    # return the epoch time of the last message sent or received
    def last_ts(self):
        return int(self.thread['messages'][-1]['internalDate']) / 1000

    # We'll need this one so that we can do matching against the contents of the mesasges we get from zillow/zumper/rentpath
    # We want to be able to populate the draft response that answers their questions they might type
    # in the site dialouge before sending it to us
    # This is going to be useful when implementing the body regex matcher
    # actually, if we are just doing a regex we don't give a shit if there's html
    # around it :)
    def generic_decode(self):
        pass
    
    # Retun a string representing the short name of the school
    # empty string if we can't find a label matching 'Schools/.*'
    def short_name(self):
        delim = 'Schools/'
        for label_id in self.field('labelIds'):
            label_name = self.service.get_label_name(label_id)
            if label_name and label_name.find(delim) == 0:
                return label_name[len(delim):]
        return 'the campus' # TODO: are we sure?

    # parse the thread created when a tenant submits their application 
    # and return the tenant email address
    def get_new_application_email(self):
        # REFACTOR: we might want to create a Message class similar to thread, in
        # which case we would have a .decode() function
        substring = '<tr><th>Email:</th><td>'
        decoded_html = self.__decode_message(0)
        start_index = decoded_html.find(substring) + len(substring)
        if start_index == -1:
            raise Exception('Could not find the substring: {} in the first message of the thread.'.format(substring))
        end_index = decoded_html[start_index:].index('<') + start_index
        return decoded_html[start_index:end_index]

    def has_existing_draft(self):
        if self.existing_draft_text():
            return True
        return False

    # Decode the payload of the message, useful when getting emails that contain a lot
    # of html formatting
    def __decode_message(self, index, ignore_old_messages=True):
        payload = self.thread['messages'][index]['payload']
        data = ''
        if 'parts' in payload:
            for part in payload['parts']:
                data += part['body']['data']
        else:
            data = payload['body']['data']
        ret = base64.urlsafe_b64decode(data.encode('UTF8')).decode('UTF8')
        if not ignore_old_messages:
            return ret
        # Here we'll filter out all the b.s. that we get in gmail when we hit 'reply'
        delimiter = '\r\n\r\nOn '
        index = ret.find(delimiter)
        if index > 0:
            return ret[:index]
        return ret

    def __is_my_email(self, test_email):
        my_email = self.service.get_email()
        if test_email.split('@')[1] in domains \
                and test_email.split('@')[0] == my_email.split('@')[0]:
            return True
        return False

    def __extract_email(self, email_string):
        return email_string.split(' ')[-1].strip('<').strip('>')

        
    # return the last non draft message
    def __last_message(self):
        for message in reversed(self.thread['messages']):
            if 'labelIds' not in message or 'DRAFT' not in message['labelIds']:
                return message
        raise Exception('No non draft messages in thread of length {}'.format(len(self.thread['messages'])))
    def existing_draft_text(self):
        if 'labelIds' in self.thread['messages'][-1] and 'DRAFT' in self.thread['messages'][-1]['labelIds']:
            return self.__decode_message(-1)
        return ''

    def existing_draft_id(self):
        if 'labelIds' in self.thread['messages'][-1] and 'DRAFT' in self.thread['messages'][-1]['labelIds']:
# We finish with a draft message, now get the DRAFT ID (which is different than a message id)
            for draft in self.service.get_drafts():
                if draft['message']['id'] == self.thread['messages'][-1]['id']:
                    return draft['id']
        return None

    def __check_destinations_match(self, new_destinations):
        if 'labelIds' in self.thread['messages'][-1] and 'DRAFT' in self.thread['messages'][-1]['labelIds']:
            for email in new_destinations:
                if not email in self.field('to', subset=self.thread['messages'][-1], default=[email]):
                    raise Exception('{} not in list of recipients for existing draft. Existing recipients are: {}'.format(email, self.field('to', subset=self.thread['messages'][-1])))
        return

    def __add_or_update_message(self, message):
        for i, old_message in enumerate(self.thread['messages']):
            if old_message['id'] == message['id']:
                self.thread['messages'][i] = message
                return
        self.thread['messages'].append(message)
                



