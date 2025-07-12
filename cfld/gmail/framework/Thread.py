import pdb
from time import time
import re

from framework.Logger import Logger
from framework.MimeEmail import create_multipart
from framework.Config import Config

def is_computer_generated_address(email: str) -> bool:
    """
    Returns True if the email looks like a random, machine-generated address.
    Heuristic approach: long mixed alphanumeric, no obvious words, high entropy.
    """
    try:
        local, domain = email.split('@')
    except ValueError:
        # Invalid email format
        return False

    # Heuristics
    if len(local) < 8:
        return False  # Too short to be machine-generated "random"

    # Count letters and digits
    letters = sum(c.isalpha() for c in local)
    digits = sum(c.isdigit() for c in local)
    specials = sum(not c.isalnum() for c in local)

    # Check if it's heavily mixed
    mixing_ratio = min(letters, digits) / max(letters, digits) if max(letters, digits) > 0 else 0

    # Contains long sequence without separators
    if re.fullmatch(r'[a-zA-Z0-9]+', local):
        # no dots/underscores => more likely random
        separators = 0
    else:
        separators = 1

    # Basic heuristics thresholds (tune as needed)
    if (letters + digits) / len(local) > 0.9 and mixing_ratio > 0.3 and separators == 0:
        return True

    # Fallback: if it's very long and all alnum
    if len(local) > 20 and separators == 0:
        return True

    return False

class Thread(Logger):
    def __init__(self, identifier, messages, service, historyId=0):
        super(Thread, self).__init__(__class__)
        self.service = service
        self.identifier = identifier
        self.messages = messages
        self.historyId = int(historyId)
        if len(self) == 0:
            raise Exception('Don\'t want to create a thread that contains no non draft messages, throwing in constructor as part of normal operation.')
        if self.messages:
            self.li('Initialized thread with id: {} subject: {}'.format(self.identifier, self.subject()))
        else:
            self.li('Initialized empty thread with id: {}'.format(self.identifier))

    def history_id(self):
        return self.historyId
    def _set_history_id(self, historyId):
        self.historyId= int(historyId)

    def subject(self):
        return self.messages[0].subject()
    def id(self):
        return self.identifier
    
    def set_label(self, label_string, unset=False):
        if self.has_label(label_string) and not unset:
            return
        elif not self.has_label(label_string) and unset:
            return
        label_id = self.service.get_label_id(label_string)
        if label_id:
            resp = self.service.set_label(self.identifier, label_id, unset)
            for message in self.messages:
                message.set_labels(resp)
    # return the number of messages in the thread that have been sent by the user
    def get_user_message_count(self):
        my_email_count = 0
        for message in self.messages:
            if self.__is_my_email(message.sender()) and not message.is_draft():
                my_email_count += 1
        return my_email_count
   
    # if thread was constructed for tom@abc.com this would return 'tom'
    def get_user_name(self):
        return self.service.get_user()

    def label_ids(self):
        return self.messages[0].label_ids()

    def has_label(self, label_string):
        return label_string in self.labels()

    def labels(self):
        labels = set()
        for message in self.messages:
            if message.is_draft():
                continue
            for label_id in message.label_ids():
                labels.add(self.service.get_label_name(label_id))
        return labels

    def __len__(self):
        if self.messages[-1].is_draft():
            return len(self.messages) - 1
        return len(self.messages)

    def __repr__(self):
        return 'thread_id: {} subject: {}'.format(self.id(), self.subject())

    def remove_existing_draft(self, delete_at_service_level=True):
        draft_id = self.existing_draft_id()
        if not draft_id:
            self.lw('No existing draft to remove. Thread id: {} subject: {}'.format(self.identifier, self.subject()))
            return
        # remove the draft from local copy
        if not self.messages[-1].is_draft():
            raise Exception('Trying to remove a draft message when the last message is telling us it\'s not a draft')
        self.messages.pop()
        if delete_at_service_level:
            self.service.delete_draft(draft_id)

    def prepend_to_draft(self, body, destinations):
        if body:
            new_body = body + self.existing_draft_text()
        else:
            new_body = self.existing_draft_text()
        self.__add_or_update_draft(new_body, destinations)

    def append_to_draft(self, body, destinations):
        new_body = self.existing_draft_text()
        if body:
            new_body += body
        self.__add_or_update_draft(new_body, destinations)

    def last_attachment(self):
        for message in reversed(self.messages):
            for attachment_data, attachment_fn in reversed(message.attachments()):
                return attachment_data, attachment_fn
        return ''
    def add_attachment_to_draft(self, data, fn, destinations):
        if not data:
            self.le('Empty attachment passed, no action will be taken')
            return
        draft_id = self.existing_draft_id()
        if draft_id:
            destinations = self.__concatenate_destinations(destinations)
        existing_body = self.existing_draft_text()
        existing_attachments = self.existing_draft_attachments()
        existing_attachments.append((data, fn))
        mime_multipart = create_multipart(destinations, self.service.get_email(), self.subject(), self.last_message().message_id(), self.last_message().message_id(), existing_body, existing_attachments)
        if draft_id:
            self.remove_existing_draft(False) # Remove our copy but not the service copy
        response = self.service.append_or_create_draft(mime_multipart, self.identifier, draft_id) # service returns a Message class
        self.__add_or_update_message(response)

    def __add_or_update_draft(self, body, destinations):
        
        self.ld('Draft will have body: {}'.format(body))
        draft_id = self.existing_draft_id()
        if draft_id:
            destinations = self.__concatenate_destinations(destinations)

        mime_multipart = create_multipart(destinations, self.service.get_email(), self.subject(), self.last_message().message_id(), self.last_message().message_id(), body, self.existing_draft_attachments())
        if draft_id:
            self.remove_existing_draft(False) # Remove our copy but not the service copy
        response = self.service.append_or_create_draft(mime_multipart, self.identifier, draft_id) # service returns a Message class
        self.__add_or_update_message(response)

    # Get the greeting we want to use for messages sent to the thread
    # If we are sending to multiple people, something like 'Hi all,\n\n'
    # For one person, 'Hi first_name,\n\n'
    # The form submitted through the website will make it easy to find their first name 
    # We would need to implement for each Zillow/RentPath/Zumper auto reach out
    # Once we have a message sent by us, we can grab the first line of the email and use that
    def salutation(self):
        # If there is a message we sent in the thread, use that
        base = 'Hi{},'
        for message in self.messages:
            if not message.is_draft() and self.__is_my_email(message.sender()):
                return message.content().split(',')[0] + ','
        # Otherwise if we have a reply-to in the first message of the thread, pull the first name from that
        reply_to = self.messages[0].reply_to(raw=True)
        if reply_to:
            return base.format(' ' + reply_to.split()[0].strip('"'))
        # Otherwise log a warning and return something generic
        self.lw('Could not find salutation in thread with id: {} subject: {}'.format(self.identifier, self.subject()))
        return base.format('')

    def signature(self):
        config = Config()
        if len(self.messages) <= 2:
            return config['long_signature']
        else:
            return config['short_signature']

    # For reply all, get everything in the from, to, and cc fields that isn't our email
    def default_reply(self, reply_all=True, force_all=False):
        counter = -1
        while True:
            message = self.messages[counter]
            counter -= 1
            if message.is_draft():
                continue
            emails = []
            # Automated mail from sites like zillow/zumper will have reply-to set
            # when this is available use it, and skip everything else
            reply_to = message.reply_to()
            if reply_to:
                emails.append(reply_to)
                # Since Adobe doesn't know how to set the 'Reply-To' header in emails they send
                # out we added a hack that optionally allows you to work around that
                if not force_all:
                    return emails
            from_email = message.sender()
            if not self.__is_my_email(from_email):
                emails.append(from_email)
            for to_email in message.recipients():
                if not self.__is_my_email(to_email):
                    emails.append(to_email)
            if reply_all:
                for cc_email in message.cc():
                    if not self.__is_my_email(cc_email):
                        emails.append(cc_email)
            return emails
                
        raise Exception('Couldn\'t find email that didn\'t match our own')

    # TODO ut
    def default_reply_str(self, prepend=True):
        ret = ''
        for email in self.default_reply():
            ret += email + ','
        if prepend:
            return ',' + ret[:-1]
        return ret[:-1]

    # Look through the string body to see what tenant gave us following the string 'email:'
    def extract_email_from_body(self):
        # at this point the last message text will be the email we are replying to, not the draft we are creating
        body = self.last_message_text()
        body = body.lower()
        needle = 'email:'
        if needle not in body:
            return []
        start = body.index(needle) + len(needle)
        # now we have the start of the email, do a regular expression to find the email
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_regex, body[start:])
        if match:
            print(match.group(0))
            return [match.group(0)]
        self.ld('Couldn\'t find email in body: {}'.format(body))
        return []

    # return the epoch time of the last message sent or received
    def last_ts(self):
        return self.last_message().ts()

    def age_in_days(self, now_f=time):
        return int((now_f() - self.last_message().ts()) / 86400)
    
    def send_draft(self):
        draft_id = self.existing_draft_id()
        if not draft_id:
            self.le('No existing draft when we are trying to send on a thread. {}'.format(self))
            return
            #raise Exception('No existing draft when we are trying to send on a thread.')
        message = self.service.send_draft(draft_id)
        if message:
            self.__add_or_update_message(message)

    def has_draft(self):
        if self.existing_draft_text():
            return True
        return False

    # Return true if the last non draft message is from our user, false otherwise
    def is_last_message_from_us(self):
        last_message = self.last_message()
        return self.__is_my_email(self.last_message().sender())

    def is_last_message_from_them(self):
        return not self.is_last_message_from_us()

    # return the decoded body of the last non draft message
    def last_message_text(self):
        return self.last_message().content()
    def first_message_text(self):
        return self.first_message().content()

    # return the decoded body of all non draft messages in the thread
    def full_text(self):
        text = ''
        for message in self.messages:
            if not message.is_draft():
                text += message.content() + '\n'
        return text[:-1]

    def __is_my_email(self, test_email):
        if not test_email:
            return False
        user = self.service.get_user()
        if test_email.split('@')[1] in self.service.get_domains() \
                and test_email.split('@')[0] == user:
            return True
        return False

    def my_emails(self):
        user = self.service.get_user()
        ret = []
        for d in self.service.get_domains():
            ret.append(user + '@' + d)
        return ret

    # return the last non draft message
    def last_message(self):
        for message in reversed(self.messages):
            if not message.is_draft():
                return message
        raise Exception('No non draft messages in thread of length {}'.format(self.__len__()))

    def first_message(self):
        for message in self.messages:
            if not message.is_draft():
                return message
        raise Exception('No non draft messages in thread of length {}'.format(self.__len__()))

    def existing_draft_text(self):
        if self.messages[-1].is_draft():
            return self.messages[-1].content()
        return ''
    def existing_draft_attachments(self):
        if self.messages[-1].is_draft():
            return self.messages[-1].attachments()
        return []

    def existing_draft_id(self):
        if self.messages[-1].is_draft():
# We finish with a draft message, now get the DRAFT ID (which is different than a message id)
            for draft in self.service.get_drafts():
                if draft['message']['id'] == self.messages[-1].id():
                    return draft['id']
        return None

    def __concatenate_destinations(self, new_destinations):
        if self.messages[-1].is_draft():
            new_destinations = list(set(new_destinations) | set(self.messages[-1].recipients()))
        at_least_one_human_email = any(not is_computer_generated_address(email) for email in new_destinations)
        if at_least_one_human_email:
            # If we have at least one human email, filter out all the computer generated emails
            new_destinations = [email for email in new_destinations if not is_computer_generated_address(email)]
        return new_destinations

    def __add_or_update_message(self, new_message):
        for i, old_message in enumerate(self.messages):
            if old_message.id() == new_message.id():
                old_message.update_all(new_message)
                return
        self.messages.append(new_message)

    def get_thread_emails(self):
        emails = []
        for message in self.messages:
            if not message.is_draft():
                emails.append(message.sender())
        return emails

    def get_thread_messages(self):
        m = []
        for message in self.messages:
            m.append(message.content())
        return m
                



