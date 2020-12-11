import pdb
from time import time

from Logger import Logger
from MimeEmail import create_multipart

# Once I get the mapping down I need to write 20 asserts for the thread class before adding more functionality
class Thread(Logger):
    def __init__(self, identifier, messages, service):
        super(Thread, self).__init__(__name__)
        self.service = service
        self.identifier = identifier
        self.messages = messages
        if self.messages:
            self.li('Initialized thread with id: {} subject: {}'.format(self.identifier, self.subject()))
        else:
            self.li('Initialized empty thread with id: {}'.format(self.identifier))

    def subject(self):
        return self.messages[0].subject()
    
    def set_label(self, label_string, unset=False):
        label_id = self.service.get_label_id(label_string)
        if label_id:
            resp = self.service.set_label(self.identifier, label_id, unset)
            for label_id in resp:
                for message in self.messages:
                    message.add_label_id(label_id)
        else:
            raise Exception('Service cannot find a label id for label: {}'.format(label_string))
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
    def labels(self):
        labels = []
        for label_id in self.messages[0].label_ids():
            labels.append(self.service.get_label_name(label_id))
        return labels

    def __len__(self):
        if self.messages[-1].is_draft():
            return len(self.messages) - 1
        return len(self.messages)

    def remove_existing_draft(self):
        draft_id = self.existing_draft_id()
        if not draft_id:
            self.lw('No existing draft to remove. Thread id: {} subject: {}'.format(self.identifier, self.subject()))
            return
        self.service.delete_draft(draft_id)
        # remove the draft from local copy
        if not self.messages[-1].is_draft():
            raise Exception('Trying to remove a draft message when the last message is telling us it\'s not a draft')
        self.messages.pop()

    def prepend_to_draft(self, body, destinations):
        new_body = body + self.existing_draft_text()
        self.__add_or_update_draft(new_body, destinations)

    def append_to_draft(self, body, destinations):
        new_body = self.existing_draft_text() + body
        self.__add_or_update_draft(new_body, destinations)

    def last_attachment(self):
        for message in reversed(self.messages):
            for attachment_data, attachment_fn in reversed(message.attachments()):
                return attachment_data, attachment_fn
        return ''
    def add_attachment_to_draft(self, data, fn, destinations):
        self.__check_destinations_match(destinations)
        if not data:
            self.le('Empty attachment passed, no action will be taken')
            return
        draft_id = self.existing_draft_id()
        self.__try_remove_draft_before_update(draft_id)

        existing_body = self.existing_draft_text()
        existing_attachments = self.existing_draft_attachments()
        existing_attachments.append((data, fn))
        mime_multipart = create_multipart(destinations, self.service.get_email(), self.subject(), self.__last_message().message_id(), self.__last_message().message_id(), existing_body, existing_attachments)

        response = self.service.append_or_create_draft(mime_multipart, self.identifier, draft_id) # service returns a Message class
        self.__add_or_update_message(response)

    def __add_or_update_draft(self, body, destinations):
        self.__check_destinations_match(destinations)
        self.ld('Draft will have body: {}'.format(body))
        draft_id = self.existing_draft_id()
        self.__try_remove_draft_before_update(draft_id)

        mime_multipart = create_multipart(destinations, self.service.get_email(), self.subject(), self.__last_message().message_id(), self.__last_message().message_id(), existing_body, self.existing_attachments)
        response = self.service.append_or_create_draft(mime_multipart, self.identifier, draft_id) # service returns a Message class
        self.__add_or_update_message(response)

    def __try_remove_draft_before_update(self, draft_id):
        if draft_id:
            if not self.messages[-1].is_draft():
                raise Exception('Trying to remove a draft message when the last message is telling us it\'s not a draft')
            self.messages.pop() # we'll get a new message id when we do a modify of a draft

        

    # Get the greeting we want to use for messages sent to the thread
    # If we are sending to multiple people, something like 'Hi all,\n\n'
    # For one person, 'Hi first_name,\n\n'
    # The form submitted through the website will make it easy to find their first name 
    # We would need to implement for each Zillow/RentPath/Zumper auto reach out
    # Once we have a message sent by us, we can grab the first line of the email and use that
    def salutation(self):
        # If there is a message we sent in the thread, use that
        base = 'Hi{},'
        for message in reversed(self.messages):
            if not message.is_draft() and self.__is_my_email(message.sender()):
                return message.content().split(',')[0] + ','
        # Otherwise if we have a reply-to in the first message of the thread, pull the first name from that
        reply_to = self.messages[0].reply_to(raw=True)
        if reply_to:
            return base.format(' ' + reply_to.split()[0])
        # Otherwise log a warning and return something generic
        self.lw('Could not find salutation in thread with id: {} subject: {}'.format(self.identifier, self.subject()))
        return base.format('')

    # Return true if we want to send a follow up email to the thread confirming that the 
    # tenant is no longer interested in housing
    # Conditions- last message was sent by userId='me' more than duration_days ago
    def need_make_them_say_no(self, duration_days=2, time_getter_f=time):
        ts_true = self.last_ts() + duration_days * 86400 < time_getter_f()
        # last message is from userId=me 
        # AND we have sent that message (as opposed to a draft)
        last_msg_true = \
            self.is_last_message_from_us() \
            and self.messages[-1].has_label_id('SENT')
        return ts_true and last_msg_true

    # For reply all, get everything in the from, to, and cc fields that isn't our email
    def default_reply(self, reply_all=True):
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

    # return the epoch time of the last message sent or received
    def last_ts(self):
        return self.messages[-1].ts()

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
        for label_id in self.messages[0].label_ids():
            label_name = self.service.get_label_name(label_id)
            if label_name and label_name.find(delim) == 0:
                return label_name[len(delim):]
        return 'the campus' # TODO: are we sure?


    def has_existing_draft(self):
        if self.existing_draft_text():
            return True
        return False

    # Return true if the last non draft message is from our user, false otherwise
    def is_last_message_from_us(self):
        last_message = self.__last_message()
        return self.__is_my_email(self.__last_message().sender())

    # return the decoded body of the last non draft message
    def last_message_text(self):
        return self.__last_message().content()

    def __is_my_email(self, test_email):
        if not test_email:
            return False
        my_email = self.service.get_email()
        if test_email.split('@')[1] in self.service.get_domains() \
                and test_email.split('@')[0] == my_email.split('@')[0]:
            return True
        return False


    # return the last non draft message
    def __last_message(self):
        for message in reversed(self.messages):
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

    # TODO: return a bool
    def __check_destinations_match(self, new_destinations):
        if self.messages[-1].is_draft():
            for email in new_destinations:
                if not email in self.messages[-1].recipients():
                    raise Exception('{} not in list of recipients for existing draft. Existing recipients are: {}'.format(email, self.messages[-1].recipients()))
        return

    def __add_or_update_message(self, new_message):
        for i, old_message in enumerate(self.messages):
            if old_message.id() == new_message.id():
                old_message.update_all(new_message)
                return
        self.messages.append(new_message)
                



